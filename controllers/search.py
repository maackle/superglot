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

	results = core.find_all_articles(current_user)
	return render_template('views/search/home.jade', articles=results)


@blueprint.route('/relevant')
@login_required
def relevant():

	results = core.find_relevant_articles(current_user)
	return render_template('views/search/home.jade', articles=results)
