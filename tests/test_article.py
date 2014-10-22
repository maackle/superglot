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
import superglot

from .base import SuperglotTestBase


class TestArticle(SuperglotTestBase):

	test_account = {'email': 'test@superglot.com', 'password': '1234'}

	def _create_article(self, user, article_def):
		with open(article_def['file'], 'r') as f:
			plaintext = f.read()
			article, created = superglot.create_article(
				user=user,
				title=article_def['title'],
				plaintext=plaintext[0:]
			)
		return article, created

	def test_create_article(self):
		import superglot
		import models

		user = self.db.session.query(models.User).first()

		for article_def in self.test_articles:
			article, created = self._create_article(user, article_def)
			eq_(
				len(article.sentence_positions.keys()),
				article_def['num_sentences']
			)

	def test_create_article_twice(self):
		import superglot
		import models

		user = self.db.session.query(models.User).first()

		article_def = self.test_articles[0]
		article, created = self._create_article(user, article_def)
		article, created = self._create_article(user, article_def)

