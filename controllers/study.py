import re
import datetime
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

from cache import cache
from controllers import api
import models
import util
import srs


blueprint = Blueprint('study', __name__, template_folder='templates')

@blueprint.route('/')
@login_required
def home():
	return render_template('views/study/home.jade')



@blueprint.route('/words/')
@login_required
def words():

	due_vocab = (item for item in current_user.vocab if item.score >= srs.SCORE_MIN and item.next_repetition and item.next_repetition < util.now())

	return render_template('views/study/study_words.jade', **{
		'due_vocab': due_vocab,
	})


@blueprint.route('/sentences/')
@login_required
def sentences():

	sentences = set()
	for article in models.TextArticle.objects.filter(user=current_user.id):
		sentences.update(set(article.gen_sentences()))

	return render_template('views/study/study_sentences.jade', **{
		"sentences": sentences	
	})