
from bs4 import BeautifulSoup
from textblob import TextBlob
import requests

from flask import Blueprint, render_template, request, jsonify
from flask.ext.login import current_user, login_required

import nlp
from models import Word

blueprint = Blueprint('api', __name__, template_folder='templates')

@blueprint.route('/')
def index():
	return 'API v1.0'

@blueprint.route('/user/words/update/', methods=['POST',])
@login_required
def update_word():
	lemma = request.form.get('lemma')
	group = request.form.get('group')

	word = Word.objects(lemma=lemma).first()

	change = current_user.update_word(word, group)
	
	if change:
		(old, new) = change
		return jsonify({'from': old, 'to': new})
	else:
		return 'false'