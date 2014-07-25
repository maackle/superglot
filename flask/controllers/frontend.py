import re
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from mongoengine.errors import NotUniqueError

from forms import AddArticleForm
from models import User, UserWordList, Word, TextArticle, WordOccurrence
from controllers import api
from util import sorted_words
import nlp
import util
import formatting



blueprint = Blueprint('frontend', __name__, template_folder='templates')

@blueprint.route('/')
def home():
	return render_template('views/home.jade')

@blueprint.route('/words/', methods=['GET', 'POST'])
@login_required
def word_list_all():
	words = current_user.words
	words.sort()
	return render_template('views/frontend/vocabulary_show.jade', words=words)

@blueprint.route('/words/<partition>/', methods=['GET', 'POST'])
@login_required
def word_list(partition):
	if partition in ('known', 'learning', 'ignored',):
		words = getattr(current_user.words, partition)
	words.sort(key=Word.sort_key)
	return render_template('views/frontend/word_list.jade', words=words)

@blueprint.route('/words/add/<partition>/', methods=['POST'])
@login_required
def add_words(partition):
	# def words(partition):
	# 	for reading, lemma in set(nlp.tokenize(request.form['words'])):
	# 		(word, created) = Word.objects.get_or_create(reading=reading, lemma=lemma)
	# 		if word:
	# 			yield word.id

	# new_words = list(words(partition))
	tokens = nlp.tokenize(request.form['words'])
	new_words = make_words(tokens)
	new_word_ids = [w.id for w in new_words]
	for name in UserWordList.group_names:
		for word_id in new_word_ids:
			if word_id in map(lambda w: w.id, getattr(current_user.words, name)):
				User.objects(id=current_user.id).update_one(**{
					"pull__words__{}".format(name): word_id
				})
	User.objects(id=current_user.id).update_one(**{
		"add_to_set__words__{}".format(partition): new_word_ids
	})
	current_user.reload()
	flash('Added some words')
	return redirect(url_for('frontend.word_list_all'))


@blueprint.route('/texts/', methods=['GET', 'POST'])
@login_required
def article_list():
	docs = list(TextArticle.objects(user=current_user.id))
	stats = [doc.word_stats(current_user.words) for doc in docs]
	return render_template('views/frontend/article_list.jade', doc_pairs=list(zip(docs, stats)))


@blueprint.route('/texts/<doc_id>/read', methods=['GET', 'POST'])
@login_required
def article_read(doc_id):
	doc = TextArticle.objects(user=current_user.id, id=doc_id).first_or_404()
	stats = doc.word_stats(current_user.words)

	def annotate(word):
		group = None
		for name in UserWordList.group_names:
			words = getattr(current_user.words, name)
			lemmata = (w.lemma for w in words)
			if word.lemma in lemmata:
				group = name
				break

		return {
			'word': word,
			'group': group,
		}

	annotated_words = list(map(annotate, doc.sorted_words()))
	
	return render_template('views/frontend/article_read.jade', 
		doc=doc, 
		stats=stats,
		annotated_words=annotated_words)


@blueprint.route('/texts/add/', methods=['GET', 'POST'])
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


	def make_words(tokens):
		# TODO: add warning if reading is case-insensitively the same, in case the user really wants
		# to add an acronym or something
		for token in tokens:
			reading, lemma = token.tup()
			try:
				(word, created) = Word.objects(reading__iexact=reading).get_or_create(
					lemma=lemma,
					language='en',
					defaults={
						'reading': reading,
					}
				)
				yield word
			except Word.MultipleObjectsReturned:
				pass


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
					occurrences[word.id] = WordOccurrence(word=word)
				occurrences[word.id].locations.append(sentence.start)
				occurrences[word.id].sentences.append(i)

		num_words_before = Word.objects.count()
		user = User.objects(id=current_user.id).first()

		duplicates = set()
		added = set()

		occ = list(occurrences.values())
		(article, created) = TextArticle.objects.get_or_create(
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

		num_words_after = Word.objects.count()
		num_added = num_words_after - num_words_before
		
		if created:
			flash("Added {}".format(title), 'success')
		else:
			flash("Updated {}".format(title), 'success')

		return redirect(url_for('frontend.article_list'))
	else:
		return render_template('views/frontend/article_create.jade', form=form)

