from flask import Blueprint, render_template, request, jsonify
from flask.ext.login import current_user

from bs4 import BeautifulSoup
from textblob import TextBlob
import requests

import nlp

blueprint = Blueprint('chrome_api', __name__, template_folder='templates')

@blueprint.route('/annotate/')
def annotate():
	url = request.form.get('url')
	
@blueprint.route('/user/')
def user():
	if current_user.is_authenticated():
		return current_user.json()
	else:
		return jsonify({})
