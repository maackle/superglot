import re
import datetime
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

from superglot.cache import cache
from controllers import api
from superglot import models
from superglot import util
from superglot import srs
from superglot import nlp
from superglot import core
from pprint import pprint

blueprint = Blueprint('study', __name__, template_folder='templates')


@blueprint.route('/')
@login_required
def home():
	return render_template('views/study/home.jade')


@blueprint.route('/words/')
@login_required
def words():

	due_vocab = core.gen_due_vocab(current_user)

	return render_template('views/study/study_words.jade', **{
		'due_vocab': due_vocab,
	})


@blueprint.route('/sentences/')
@login_required
def sentences():
	W = models.Word
	V = models.VocabWord
	O = models.WordOccurrence
	# all_vocab = set(filter(lambda item: item.rating is not 0, current_user.vocab))
	all_vocab = set(current_user.vocab)

	due_vocab = list(superglot.gen_due_vocab(current_user))
	due_words = set(map(lambda item: item.word, due_vocab))

	sentences = list()
	for article in models.Article.query().filter_by(user_id=current_user.id):
		for sentence in core.get_article_sentences(article, due_words):
			tokens = nlp.tokenize(sentence)
			lemmata = (tok.lemma for tok in tokens)
			pairs = (
				app.db.session.query(V, O)
				.join(W)
				.filter(V.word_id == O.word_id)
				.filter(W.lemma.in_(lemmata))
			)
			vocabmap = util.dict_from_seq(
				pairs,
				lambda p: p[0].word.lemma
			)
			vocab = []
			for tok in tokens:
				# if not found, the token doesn't represent a Word
				vocab_pair = vocabmap.get(tok.lemma)
				if vocab_pair:
					vocab.append(vocab_pair)
			sentences.append( (sentence, vocab) )

	return render_template('views/study/study_sentences.jade', **{
		"due_vocab": due_vocab,
		"sentences": sentences
	})


@blueprint.route('/all/')
@login_required
def all():

	due_vocab = core.gen_due_vocab(current_user)

	return render_template('views/study/study_all.jade', **{
		'due_vocab': due_vocab,
	})
