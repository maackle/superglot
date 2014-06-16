import re
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from mongoengine.errors import NotUniqueError

from forms import AddArticleForm
from models import User, UserWordList, Word, TextArticle
from controllers import api
from util import sorted_words
import nlp
import util
import formatting


def make_words(tokens):
	# TODO: add warning if reading is case-insensitively the same, in case the user really wants
	# to add an acronym or something
	for reading, lemma in set(tokens):
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
	new_words = make_words(nlp.tokenize(request.form['words']))
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
	return render_template('views/frontend/article_list.jade', doc_pairs=zip(docs, stats))


@blueprint.route('/texts/<doc_id>/read', methods=['GET', 'POST'])
@login_required
def article_read(doc_id):
	doc = TextArticle.objects(user=current_user.id, id=doc_id).first_or_404()
	stats = doc.word_stats(current_user.words)

	def annotate(word):
		group = None
		for name in UserWordList.group_names:
			if word in getattr(current_user.words, name):
				group = name
				break

		if not group:
			print(word)

		print(sorted(list(map(lambda w: w.lemma, current_user.words.known))))
		return {
			'word': word,
			'group': group,
		}

	annotated_words = map(annotate, doc.sorted_words())
	
	return render_template('views/frontend/article_read.jade', 
		doc=doc, 
		stats=stats,
		annotated_words=annotated_words)


@blueprint.route('/texts/add/', methods=['GET', 'POST'])
@login_required
def article_create():
	form = AddArticleForm(url='http://michaeldougherty.info')
	if form.validate_on_submit():
		ignored_tags = ['script', 'style', 'code', 'head', 'iframe']
		url = form.url.data
		req = util.get_page(url)
		soup = BeautifulSoup(req.text)
		if soup.title:
			title = soup.title.string
		elif form.title:
			title = form.title.data
		elif url:
			title = url
		else:
			title = "[UNTITLED]"

		# remove noisy content-empty tags
		for tag in ignored_tags:
			for t in soup(tag):
				t.decompose()

		plaintext = "\n".join(soup.stripped_strings)
		tokens = nlp.tokenize(plaintext)
		words = list(make_words(tokens))
		num_words_before = Word.objects.count()
		user = User.objects(id=current_user.id).first()

		duplicates = set()
		added = set()

		(article, created) = TextArticle.objects.get_or_create(
			source=url,
			user=user,
			defaults={
				'title': title,
				'words': words,
				'plaintext': plaintext,
				}
			)
		if not created:
			article.words = words
			article.title = title
			article.plaintext = plaintext
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

