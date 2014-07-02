
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
	lemmata = request.form.get('lemmata').split('\n')
	group = request.form.get('group')

	changes = []

	for lemma in lemmata:

		word = Word.objects(lemma=lemma).first()
		change = current_user.update_word(word, group)
		
		if change:
			(old, new) = change
			changes.append({'from': old, 'to': new})
		else:
			changes.append('false')
	print(changes)

	return jsonify({'changes': changes})