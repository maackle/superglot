import re
import datetime
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

from cache import cache
from controllers import api
import models
import util
import srs
import nlp


blueprint = Blueprint('study', __name__, template_folder='templates')

def gen_due_vocab():
	return (item for item in current_user.vocab if item.rating >= srs.RATING_MIN and item.srs_next_repetition and item.srs_next_repetition < util.now())


@blueprint.route('/')
@login_required
def home():
	return render_template('views/study/home.jade')


@blueprint.route('/words/')
@login_required
def words():

	due_vocab = gen_due_vocab()

	return render_template('views/study/study_words.jade', **{
		'due_vocab': due_vocab,
	})


@blueprint.route('/sentences/')
@login_required
def sentences():

	# all_vocab = set(filter(lambda item: item.rating is not 0, current_user.vocab))
	all_vocab = set(current_user.vocab)

	due_vocab = list(gen_due_vocab())
	due_words = set(map(lambda item: item.word, due_vocab))

	sentences = list()
	for article in models.TextArticle.objects.filter(user=current_user.id):
		for sentence in article.gen_sentences(due_words):
			sentence_vocab_list = list(models.VocabWord(word=token.word()) for token in nlp.tokenize(sentence))
			sentence_vocab_set = all_vocab | set(sentence_vocab_list)
			sentence_vocab = list()
			for item in sentence_vocab_list:
				# items = sentence_vocab_set & set((item,))  # this doesn't work, so...
				items = set(filter(lambda i: i == item, sentence_vocab_set))
				try:
					annotated_item = items.pop()
				except KeyError:
					app.logger.info(sentence_vocab_set)
					app.logger.info(item)
					raise
				# TODO: use actual reading, not lemma!
				sentence_vocab.append(annotated_item)
			sentences.append( (sentence, sentence_vocab) )
			# break  # TODO!!

	return render_template('views/study/study_sentences.jade', **{
		"due_vocab": due_vocab,
		"sentences": sentences
	})


@blueprint.route('/all/')
@login_required
def all():

	due_vocab = gen_due_vocab()

	return render_template('views/study/study_all.jade', **{
		'due_vocab': due_vocab,
	})
