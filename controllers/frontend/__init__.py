import re
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _

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



blueprint = Blueprint('frontend', __name__, template_folder='templates')

@blueprint.route('/')
def home():
	return render_template('views/home.jade')
