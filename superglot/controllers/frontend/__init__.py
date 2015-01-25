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



blueprint = Blueprint('frontend', __name__, template_folder='templates')

@blueprint.route('/')
def home():
	return render_template('views/home.jade')
