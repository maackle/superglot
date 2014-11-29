import re
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

from superglot.cache import cache
from superglot.forms import AddArticleForm
from superglot import models
from controllers import api
from superglot.util import sorted_words
from superglot import nlp
from superglot import util
import formatting
from config import settings
from superglot import core
from pprint import pprint



blueprint = Blueprint('frontend.words', __name__, template_folder='templates')


@blueprint.route('/user/words/', methods=['GET', 'POST'])
@login_required
def word_list_all():
	vocab = list(current_user.vocab)
	return render_template('views/frontend/vocab_show.jade', vocab=vocab)

@blueprint.route('/user/words/delete/', methods=['GET', 'POST'])
@login_required
def delete_all_words():
	current_user.delete_all_words()
	flash(_('Deleted all words!'))
	return redirect(url_for('frontend.words.word_list_all'))

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
	if label == 'ignored':
		rating = settings.RATING_VALUES['ignored']
	elif label == 'learning':
		rating = settings.RATING_VALUES['learning']
	elif label == 'known':
		rating = settings.RATING_VALUES['known']
	else:
		raise "Invalid label"
	tokens = nlp.tokenize(request.form['words'])
	new_words = core.gen_words_from_tokens(tokens)
	updated, ignored = core.update_user_words(current_user, new_words, rating)
	if updated == 0:
		flash('None of those words were recognized :(')
	else:
		flash('updated {}, ignored {}'.format(updated, ignored))
	return redirect(url_for('frontend.words.word_list_all'))
