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
	for token in set(tokens):
		(word, created) = Word.objects.get_or_create(
			reading=str(token),
			lemma=token.lemma.lower(),
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
		for token in set(nlp.tokenize(request.form['words'])):
			word = Word.find_by_reading(token)
			print(word)
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
	return render_template('frontend/document_read.jade', doc=doc)

@blueprint.route('/docs/add/', methods=['GET', 'POST'])
@login_required
def document_create():
	form = AddDocumentForm(url='http://michaeldougherty.info')
	if form.validate_on_submit():
		ignored_tags = ['script', 'code', 'head', 'iframe']
		url = form.url.data
		req = util.get_page(url)
		soup = BeautifulSoup(req.text)
		title = soup.title.string if soup.title else url

		for tag in ignored_tags:
			for t in soup(tag):
				t.decompose()

		text = "\n".join(soup.stripped_strings)
		tokens = nlp.tokenize(text)
		words = list(make_words(tokens))
		num_words_before = Word.objects.count()
		user = User.objects(id=current_user.id).first()

		duplicates = set()
		added = set()

		try:
			(article, created) = TextArticle.objects.get_or_create(
				title=title,
				source=url,
				user=user,
				defaults={
					'words': words,
					'plaintext': text,
					}
				)
			# TextArticle.objects.insert(article)

		except NotUniqueError as e:
			pass

		# try:
		# 	# words = Word.objects.insert(list(make_words(tokens)), load_bulk=False, write_concern={'continueOnInsertSDFError': True})
		# except NotUniqueError as e:
		# 	print(e)
		# 	pass

		num_words_after = Word.objects.count()
		num_added = num_words_after - num_words_before
		# User.objects(id=current_user.id).update_one(add_to_set__lemmata__known=lemmata)
		# current_user.reload()
		# current_user.lemmata.extend(lemmata)
		# current_user.save()
		
		return str((num_added, num_words_after)) + text
		# return str(map(str, Word.objects()))
	else:
		return render_template('frontend/document_create.jade', form=form)

