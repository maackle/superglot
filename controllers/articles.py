import re
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _
from mongoengine.errors import NotUniqueError

from forms import AddArticleForm
from models import User, UserWordList, Word, TextArticle
from controllers import api
from util import sorted_words
import nlp
import util


def make_words(tokens):
	for reading, lemma in set(tokens):
		(word, created) = Word.objects.get_or_create(
			reading=reading,
			lemma=lemma,
			language='en',
		)
		yield word

blueprint = Blueprint('frontend', __name__, template_folder='templates')

@blueprint.route('/')
def home():
	return render_template('views/home.jade')

@blueprint.route('/words/', methods=['GET', 'POST'])
@login_required
def word_list():
	words = current_user.words
	words.sort()
	return render_template('views/frontend/word_list.jade', words=words)

@blueprint.route('/words/add/<label>/', methods=['POST'])
@login_required
def add_words(label):
	def words(label):
		for reading, lemma in set(nlp.tokenize(request.form['words'])):
			word = Word.objects(reading=reading, lemma=lemma).first()
			if word:
				yield word.id

	new_words = list(words(label))
	for name in UserWordList.group_names:
		for word_id in new_words:
			if word_id in map(lambda w: w.id, getattr(current_user.words, name)):
				User.objects(id=current_user.id).update_one(**{
					"pull__words__{}".format(name): word_id
				})
	User.objects(id=current_user.id).update_one(**{
		"add_to_set__words__{}".format(label): new_words
	})
	current_user.reload()
	flash('Added some words')
	return redirect(url_for('frontend.word_list'))


@blueprint.route('/docs/', methods=['GET', 'POST'])
@login_required
def article_list():
	docs = list(TextArticle.objects(user=current_user.id))
	stats = [doc.word_stats(current_user) for doc in docs]
	return render_template('views/frontend/article_list.jade', doc_pairs=zip(docs, stats))


@blueprint.route('/docs/<doc_id>/read', methods=['GET', 'POST'])
@login_required
def article_read(doc_id):
	doc = TextArticle.objects(user=current_user.id, id=doc_id).first_or_404()
	stats = doc.word_stats(current_user)

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


@blueprint.route('/docs/add/', methods=['GET', 'POST'])
@login_required
def article_create():
	form = AddArticleForm(url='http://michaeldougherty.info')
	if form.validate_on_submit():
		ignored_tags = ['script', 'style', 'code', 'head', 'iframe']
		url = form.url.data
		req = util.get_page(url)
		soup = BeautifulSoup(req.text)
		title = soup.title.string if soup.title else url

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
			flash(_("added %(doc)s", title).capitalize(), 'success')
		else:
			flash(_("updated %(doc)s", title).capitalize(), 'success')

		return redirect(url_for('frontend.article_list'))
	else:
		return render_template('views/frontend/article_create.jade', form=form)

