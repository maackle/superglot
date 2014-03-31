import re
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from mongoengine.errors import NotUniqueError

from forms import AddDocumentForm
from models import User, Word, TextArticle
from controllers import api
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
	return render_template('home.jade')

@blueprint.route('/words/', methods=['GET', 'POST'])
@login_required
def word_list():
	print(current_user.words)
	return render_template('frontend/word_list.jade', words=current_user.words)

@blueprint.route('/words/add/<partition>/', methods=['POST'])
@login_required
def add_words(partition):
	def words(partition):
		for reading, lemma in set(nlp.tokenize(request.form['words'])):
			word = Word.objects(reading=reading, lemma=lemma).first()
			if word:
				yield word.id
	new_words = list(words(partition))
	User.objects(id=current_user.id).update_one(**{
		"add_to_set__words__{}".format(partition): new_words
	})
	current_user.reload()
	flash('Added some words')
	return redirect(url_for('frontend.word_list'))


@blueprint.route('/docs/', methods=['GET', 'POST'])
@login_required
def document_list():
	docs = list(TextArticle.objects(user=current_user.id))
	return render_template('frontend/document_list.jade', docs=docs)


@blueprint.route('/docs/<doc_id>/read', methods=['GET', 'POST'])
@login_required
def document_read(doc_id):
	doc = TextArticle.objects(user=current_user.id, id=doc_id).first_or_404()
	return render_template('frontend/document_read.jade', 
		doc=doc, 
		sorted_words=doc.sorted_words())


@blueprint.route('/docs/add/', methods=['GET', 'POST'])
@login_required
def document_create():
	form = AddDocumentForm(url='http://michaeldougherty.info')
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
			flash("Added {}".format(title), 'success')
		else:
			flash("Updated {}".format(title), 'success')

		return redirect(url_for('frontend.document_list'))
	else:
		return render_template('frontend/document_create.jade', form=form)

