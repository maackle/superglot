'''
Complex queries, calculations, etc.
'''

from flask import current_app as app
from bs4 import BeautifulSoup

import nlp
from cache import cache
import util
import models
import database

try:
	with database.session() as session:
		english = session.query(models.Language).filter_by(code='en').first()
except:
	print("WARNING: tried to access Language model without schema")
	english = None

def add_word(session, reading, lemma, language=english):
	word = models.Word(lemma=lemma, language_id=english.id, canonical=False)
	session.add(word)
	session.add(models.LemmaReading(lemma=lemma, reading=reading))
	return word

def fetch_remote_article(url):
	ignored_tags = ['script', 'style', 'code', 'head', 'iframe']
	req = util.get_page(url)
	soup = BeautifulSoup(req.text)

	# remove noisy content-empty tags
	for tag in ignored_tags:
		for t in soup(tag):
			t.decompose()

	strings = (soup.stripped_strings)
	strings = (map(lambda x: re.sub(r"\s+", ' ', x), strings))
	plaintext = "\n".join(strings)
	return (plaintext, soup.title)

@cache.memoize()
def get_common_words(user, article):
	'''
	Get words that show up in user's vocab and the article
	'''

	V = models.VocabWord
	O = models.WordOccurrence
	return app.db.session.query(V).\
			join(O, V.word_id == O.word_id and O.article_id == article_id).\
			filter(V.user_id==user.id).\
			all()

def gen_words_from_tokens(tokens):
	'''
	Look up words from token objects. If not in database, create a "non-canonical" word

	TODO: actually create the non-canonical word.
	'''
	for chunk in util.chunks(tokens, 500):
		words = []
		for token in chunk:
			reading, lemma = token.tup()
			word = app.db.session.query(models.Word).filter_by(lemma=lemma, language_id=english.id).first()
			if not word:
				word = models.Word(lemma=lemma, language_id=english.id, canonical=False)
			words.append(word)
		# try:
		# 	db.session.add_all(words)
		# 	db.session.commit()
		# except:
		# 	# raise
		for word in words:
			yield word

def create_article(user, title, plaintext, url=None):
	all_tokens = list()

	sentence_positions = {}
	occurrences = []
	for i, sentence in enumerate(nlp.get_sentences(plaintext)):
		sentence_positions[sentence.start] = len(sentence)
		sentence_tokens = nlp.tokenize(sentence.string)
		for word in gen_words_from_tokens(sentence_tokens):
			if word.id:
				occurrence = models.WordOccurrence(word_id=word.id, article_sentence_start=sentence.start)
				occurrences.append(occurrence)
		all_tokens.extend(sentence_tokens)

	article = models.Article(
		source=url,
		user_id=user.id,
		title=title,
		plaintext=plaintext,
		sentence_positions=sentence_positions,
	)

	app.db.session.add(article)
	app.db.session.commit()

	for o in occurrences:
		o.article_id = article.id
		app.db.session.add(o)
	app.db.session.commit()

	# cache.delete_memoized(get_common_words, user=user, article=article)

	return article, True


def authenticate_user(email, password):
	# with database.session() as session:
	user = app.db.session.query(models.User).filter_by(email=email, password=password).first()
	return user

def register_user(email, password):
	with database.session() as session:
		user = session.query(models.User).filter_by(email=email).first()
		if user:
			created = False
		else:
			user = models.User(email=email, password=password)
			session.add(user)
			session.commit()
			created = True
	return (user, created)

def update_user_words(user, words, rating):
	created = 0
	updated = 0
	ignored = 0
	for word in words:
		if word.id:
			vocab_word = user.vocab.filter_by(word_id=word.id).first()
			if vocab_word:
				vocab_word.rating = rating
				app.db.session.merge(vocab_word)
				updated += 1
			else:
				vocab_word = models.VocabWord(user_id=user.id, word_id=word.id, rating=rating)
				app.db.session.add(vocab_word)
				created += 1
		else:
			ignored += 1
	app.db.session.commit()
	return created, updated, ignored


#############################################################

def get_article_sentences(article, words):
	'''Get all sentences that contain these words'''

	indices = """
	SELECT sentence_start from word_occurrence
	WHERE word_id IN ({word_ids}) AND article_id = {article.id}
	"""
	sentences = list()
	for start in indices:
		sentence_text = article.plaintext[start:end]
		sentences.append(sentence_text)
	return sentences

def find_relevant_articles(user):

	"""SELECT
	( # this subquery seems mostly right
		SELECT v.rating, v.word_id, o.article_id from word_occurrence as o
		JOIN vocab_word as v ON (word_id = o.word_id)
		WHERE v.user_id = {user.id}
		GROUP BY o.article_id
	) as a
	WHERE count(a.rating >= 4) > { T_OK }
	ORDER BY count(a.rating > 4) / count(a.rating < 2)  # horribly wrong, but for example.
	"""

	"""
	OK   - solid, well-known words
	EDGE - words "on the edge", about to be forgotten
	BAD  - newly learned or failed words
	X    - unmarked words

	T_OK - percentage of OK words needed for easy reading

	Filter factors:
	- P(OK) > T_OK

	Sorting factors:
	- P(X) is high
	- P(EDGE) is high
	- P(OK|EDGE) / P(BAD) ratio is decent 

	possible utility functions:

	f = P(OK|EDGE|BAD) * P(OK|EDGE) / P(BAD)
	f = percent(rating >= 4) > 0.6 AND 0.1 < percent(1 <= rating <= 2) < 0.3

	"""
