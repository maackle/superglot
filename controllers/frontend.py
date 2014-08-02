import re
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _
from mongoengine.errors import NotUniqueError

from cache import cache
from forms import AddArticleForm
import models
from controllers import api
from util import sorted_words
import nlp
import util
import formatting



def make_words(tokens):
	# TODO: add warning if reading is case-insensitively the same, in case the user really wants
	# to add an acronym or something
	for token in tokens:
		reading, lemma = token.tup()
		try:
			(word, created) = models.Word.objects(reading__iexact=reading).get_or_create(
				lemma=lemma,
				language='en',
				defaults={
					'reading': reading,
				}
			)
			yield word
		except models.Word.MultipleObjectsReturned:
			pass


blueprint = Blueprint('frontend', __name__, template_folder='templates')

@blueprint.route('/')
def home():
	return render_template('views/home.jade')

@blueprint.route('/user/words/', methods=['GET', 'POST'])
@login_required
def word_list_all():
	vocab = current_user.vocab_lists()
	return render_template('views/frontend/vocab_show.jade', vocab=vocab)

@blueprint.route('/user/words/delete/', methods=['GET', 'POST'])
@login_required
def delete_all_words():
	current_user.delete_all_words()
	flash(_('Deleted all words!'))
	return redirect(url_for('frontend.word_list_all'))

@blueprint.route('/user/words/<partition>/', methods=['GET', 'POST'])
@login_required
def word_list(partition):
	vocab = current_user.vocab_lists()
	words = vocab[partition]
	words.sort(key=models.Word.sort_key)
	return render_template('views/frontend/word_list.jade', words=words)

@blueprint.route('/user/words/add/<label>/', methods=['POST'])
@login_required
def add_words(label):
	tokens = nlp.tokenize(request.form['words'])
	new_words = make_words(tokens)
	current_user.update_words(new_words, label)
	flash('Added some words')
	return redirect(url_for('frontend.word_list_all'))


@blueprint.route('/user/texts/', methods=['GET', 'POST'])
@login_required
def article_list():
	docs = list(models.TextArticle.objects(user=current_user.id))
	stats = [doc.word_stats(current_user) for doc in docs]
	return render_template('views/frontend/article_list.jade', doc_pairs=list(zip(docs, stats)))


@blueprint.route('/user/texts/<doc_id>/read', methods=['GET', 'POST'])
@login_required
def article_read(doc_id):
	'''
	TODO: words with the same lemma are not marked as known
	'''
	doc = models.TextArticle.objects(user=current_user.id, id=doc_id).first_or_404()
	stats = doc.word_stats(current_user)

	# doc_vocab = set(map(lambda word: models.AnnotatedDocWord(word=word), doc.words))
	# user_vocab = set(map(lambda item: models.AnnotatedDocWord(word=item.word, label=item.label), current_user.vocab))
	doc_vocab = set(map(lambda word: models.VocabWord(word=word), doc.words))
	user_vocab = set(current_user.vocab)
	doc_vocab = (user_vocab | doc_vocab) - (user_vocab - doc_vocab)
	
	return render_template('views/frontend/article_read.jade', 
		doc=doc, 
		stats=stats,
		annotated_words=sorted(doc_vocab))


@blueprint.route('/user/texts/add/', methods=['GET', 'POST'])
@login_required
def article_create():

	def read_page(url):
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

	form = AddArticleForm()
	if form.validate_on_submit():
		url = form.url.data
		title = form.title.data
		plaintext = None

		if form.plaintext.data:
			plaintext = form.plaintext.data
			
		if url:
			(page_text, page_title) = read_page(url)
			if not plaintext:
				plaintext = page_text
			if not title:
				title = page_title

		if not title:
			if url:
				title = url
			else:
				title = '[untitled]'

		all_tokens = set(nlp.tokenize(plaintext))
		all_words = list(make_words(all_tokens))
		sentence_positions = []
		occurrences = {}
		for i, sentence in enumerate(nlp.get_sentences(plaintext)):
			sentence_tokens = nlp.tokenize(sentence.string)
			sentence_words = list(make_words(sentence_tokens))
			sentence_positions.append((sentence.start, sentence.end))
			for word in sentence_words:
				reading = word.reading
				location = 0
				if not word.id in occurrences:
					occurrences[word.id] = models.WordOccurrence(word=word)
				occurrences[word.id].locations.append(sentence.start)
				occurrences[word.id].sentences.append(i)

		num_words_before = models.Word.objects.count()
		user = models.User.objects(id=current_user.id).first()

		duplicates = set()
		added = set()

		occ = list(occurrences.values())
		(article, created) = models.TextArticle.objects.get_or_create(
			source=url,
			user=user,
			defaults={
				'title': title,
				'words': all_words,
				'plaintext': plaintext,
				'occurrences': occ,
				'sentence_positions': sentence_positions,
				}
			)
		if not created:
			article.words = all_words
			article.title = title
			article.plaintext = plaintext
			article.occurrences = occ
			article.sentence_positions = sentence_positions
			article.save()

		num_words_after = models.Word.objects.count()
		num_added = num_words_after - num_words_before
		
		if created:
			flash("Added {}".format(title), 'success')
		else:
			flash("Updated {}".format(title), 'success')

		return redirect(url_for('frontend.article_list'))
	else:
		return render_template('views/frontend/article_create.jade', form=form)

