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


class TestWords(SuperglotTestBase):
	
	test_articles = [
		{
			'file': 'data/articles/little-prince-1.txt',
			'num_sentences': 34,
		}
	]

	def test_common_words(self):

		user = self.db.session.query(models.User).first()

		with open(self.test_articles[0]['file'], 'r') as f:
			plaintext = f.read()
			article, created = superglot.create_article(user=user, title="The Little Prince Ch. 1", plaintext=plaintext[0:1000])
		
		tokens = nlp.tokenize(plaintext)
		words = superglot.gen_words_from_tokens(tokens)
		created, updated, ignored = superglot.update_user_words(user, words, 3)
		common_words = list(superglot.get_common_words(user, article))

		eq_(created, len(common_words))

		