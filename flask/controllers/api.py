from flask import Blueprint, render_template, request

from bs4 import BeautifulSoup
from textblob import TextBlob
import requests

import nlp

blueprint = Blueprint('api', __name__, template_folder='templates')

@blueprint.route('/')
def index():
	return 'API v1.0'
