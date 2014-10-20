import re
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, abort, render_template, request, flash, redirect, url_for, current_app as app
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
from config import settings
import superglot
from pprint import pprint


blueprint = Blueprint('frontend.articles', __name__, template_folder='templates')

@blueprint.route('/user/texts/', methods=['GET', 'POST'])
@login_required
def article_list():
	articles = list(app.db.session.query(models.Article).filter_by(user_id=current_user.id))
	def stats():
		for article in articles:
			common = superglot.get_common_vocab(current_user, article)
			yield util.vocab_stats(common)
	return render_template('views/frontend/article_list.jade', article_pairs=list(zip(articles, stats())))


@blueprint.route('/user/texts/<article_id>/read', methods=['GET', 'POST'])
@login_required
def article_read(article_id):
	'''
	TODO: words with the same lemma are not marked as known
	'''
	article = app.db.session.query(models.Article).filter_by(user_id=current_user.id, id=article_id).first()
	if not article:
		abort(404)
	article_vocab = superglot.get_common_vocab(current_user, article)
	stats = util.vocab_stats(article_vocab)
	pprint(article_vocab)
	pprint(stats)

	return render_template('views/frontend/article_read.jade', 
		article=article, 
		stats=stats,
		annotated_words=sorted(article_vocab))



@blueprint.route('/user/texts/<article_id>/delete/', methods=['GET', 'POST'])
@login_required
def article_delete(article_id):
	'''
	TODO: ensure the user owns the article!!
	'''
	article = app.db.session.query(models.Article).filter_by(id=article_id).first()
	if article:
		flash(_('Deleted "%(title)s"', title=article.title))
		app.db.session.delete(article)
		app.db.session.commit()
	return redirect(url_for('.article_list'))

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

		article, created = superglot.create_article(
			user=current_user,
			title=title,
			plaintext=plaintext,
			url=url,
		)

		cache.delete_memoized(superglot.get_common_words, current_user, article)

		if created:
			flash("Added {}".format(title), 'success')
		else:
			flash("Updated {}".format(title), 'success')

		return redirect(url_for('frontend.articles.article_list'))
	else:
		return render_template('views/frontend/article_create.jade', form=form)

