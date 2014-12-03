from nose.tools import *
import io
import os
from unittest import mock
import requests

from flask import url_for
from datetime import datetime, timedelta

from superglot import models
from superglot import nlp
from superglot import util
from superglot import core

from .base from superglot import coreTestBase


class TestArticle(SuperglotTestBase):

	test_account = {'email': 'test@superglot.com', 'password': '1234'}

	def test_create_article(self):
		from superglot import core
		from superglot import models

		user = self.get_user()

		for article_def in self.test_articles:
			article, created = self._create_article(user, article_def)
			eq_(
				len(article.sentence_positions.keys()),
				article_def['num_sentences']
			)

	def test_create_article_twice(self):
		from superglot import core
		from superglot import models

		user = self.db.session.query(models.User).first()

		article_def = self.test_articles[0]
		article, created = self._create_article(user, article_def)
		article, created = self._create_article(user, article_def)

	def test_article_stats(self):

		user = self.get_user()
		article_def = self.test_articles[0]
		article, created = self._create_article(user, article_def)
		words = models.Word.query().all()
		core.update_user_words(user, words[0:10], 3)
		core.compute_article_stats(user, article)
