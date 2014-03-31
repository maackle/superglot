from flask import Blueprint, render_template, request

from bs4 import BeautifulSoup
from textblob import TextBlob
import requests

import nlp

blueprint = Blueprint('api', __name__, template_folder='templates')

@blueprint.route('/')
def index():
	return 'API v1.0'

# @blueprint.route('/tokenize/')
# def tokenize(url=None):
# 	url = url or request.args.get('url')
# 	if url:
# 		req = requests.get(url)
# 		soup = BeautifulSoup(req.text)
# 		text = soup.get_text()
# 		lemmata = set(nlp.lemmatize(text))
# 		# for l in lemmata:
# 		# 	print(l)
# 		print(type(lemmata))
# 		return "LEMMATA" + str(lemmata)
# 	else:
# 		return "invalid"