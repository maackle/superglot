import re
import sys

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

from sqlalchemy.sql.expression import func
from superglot.cache import cache
from superglot import models
from superglot import util
from superglot import srs
from superglot import nlp
from superglot import core
from pprint import pprint

blueprint = Blueprint('search', __name__, template_folder='templates')


@blueprint.route('/')
@login_required
def home():
	return render_template('views/search/home.jade', articles=[])

@blueprint.route('/')
@login_required
def postgres_search():

	A = models.Article
	O = models.WordOccurrence
	V = models.VocabWord

	user = models.User.query().first()
	core.create_article(
		user=user,
		title="sample 1",
		plaintext="good water should be used often",
	)
	core.create_article(
		user=user,
		title="sample 2",
		plaintext="we know important information",
	)
	core.create_article(
		user=user,
		title="sample 1",
		plaintext="painting politics extra attention",
	)

	core.update_user_lemmata(
		user=user,
		lemmata=[
			'good', 'water', 'information',
		],
		rating=1
	)

	core.update_user_lemmata(
		user=user,
		lemmata=[
			'painting', 'politics',
		],
		rating=2
	)

	core.update_user_lemmata(
		user=user,
		lemmata=[
			'often', 'know',
		],
		rating=3
	)

	breakdown = (
		models.query(
			A.id.label('article_id'),
			A.title,
			V.rating.label('rating'),
			func.count(V.word_id).label('count'),
		)
		.join(O, O.article_id == A.id)
		.join(V, V.word_id == O.word_id)
		.filter(V.user_id == user.id)
		.group_by(A.id, V.rating)
	)

	subquery = breakdown.subquery()
	bq = breakdown.subquery()

	totals = (
		models.query(
			bq.c.article_id.label('article_id'),
			func.sum(bq.c.count).label('total'),
		)
		.group_by(bq.c.article_id)
	)

	tq = totals.subquery()

	percents = (
		models.query(
			A.id,
			A.title,
			bq.c.rating.label('rating'),
			(bq.c.count / tq.c.total).label('percent'),
		)
		.join(bq, bq.c.article_id == A.id)
		.join(tq, tq.c.article_id == A.id)
	)

	pprint(breakdown.all())
	pprint(totals.all())

	pprint(percents.all())

	# percents = (
	# 	models.query(

	# 		func.sum(subquery.c.count).label('total'),
	# 	)
	# )

	# good = breakdown.filter(V.rating == 3)

	articles = (
		models.query(A)
		.join(subquery, A.id == subquery.c.article_id)
		.filter(subquery.c.rating == 2)
		.filter(subquery.c.count > 0)
	)

	return render_template('views/search/home.jade', articles=articles)
