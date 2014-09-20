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


blueprint = Blueprint('study', __name__, template_folder='templates')

@blueprint.route('/')
def home():
	return render_template('views/study/home.jade')



@blueprint.route('/words/')
def words():

	return render_template('views/study/study_words.jade', **{
		
	})


@blueprint.route('/sentences/')
def sentences():

	sentences = set()
	for article in models.TextArticle.objects.filter(user=current_user.id):
		sentences.update(set(article.gen_sentences()))

	return render_template('views/study/study_sentences.jade', **{
		"sentences": sentences	
	})