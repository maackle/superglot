import re

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

from cache import cache
import models
import util
import srs
import nlp
import superglot
from pprint import pprint

blueprint = Blueprint('search', __name__, template_folder='templates')


@blueprint.route('/')
@login_required
def home():
	articles = superglot.find_relevant_articles(current_user)
	return render_template('views/search/home.jade', articles=articles)
