from nose.tools import *
import io
import os
from unittest import mock
import requests

from flask import url_for
from datetime import datetime, timedelta

import models
import nlp
import util

from .base import SuperglotTestBase


class TestArticle(SuperglotTestBase):
	
	test_account = {'email': 'test@superglot.com', 'password': '1234'}

	test_articles = [
		{
			'file': 'data/articles/little-prince-1.txt',
			'num_sentences': 34,
		}
	]

	def test_create_article(self):
		import superglot
		import models

		user = self.db.session.query(models.User).first()

		for article_def in self.test_articles:
			with open(article_def['file'], 'r') as f:
				plaintext = f.read()
				article = superglot.create_article(user=user, title="Moby Dick", plaintext=plaintext[0:])
				eq_(
					len(article.sentence_positions.keys()), 
					article_def['num_sentences']
				)
				
