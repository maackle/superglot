
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
	score = request.form.get('score')
	score = int(score)

	changes = []

	for lemma in lemmata:
		word = Word.objects(lemma=lemma).first()
		change = current_user.update_words([word], score)
		
		if change:
			changes.append({
				'lemma': lemma, 
				'score': score,
			})
		else:
			changes.append('false')

	return jsonify({'changes': changes})


@blueprint.route('/words/translate/', methods=['GET',])
@login_required
def translate_word():
	word_id = request.args.get("word_id")

	word = Word.objects(id=word_id).first()
	meaning = word.lookup(current_user.native_language)

	return jsonify({
		'source_language': word.language,
		'source': word.reading,
		'target_language': meaning.language,
		'target': meaning.meaning,
	})