from nose.tools import *
import io
import os
from unittest import mock
import requests
from pprint import pprint

from flask import url_for
from datetime import datetime, timedelta

import models
import nlp
import util
import superglot

from .base import SuperglotTestBase


class TestWords(SuperglotTestBase):

	def test_common_words(self):

		user = self.db.session.query(models.User).first()
		article_def = self.test_articles[0]

		with open(article_def['file'], 'r') as f:
			plaintext = f.read()
			article, created = superglot.create_article(user=user, title=article_def['title'], plaintext=plaintext)
		
		tokens = nlp.tokenize(plaintext)
		words = superglot.gen_words_from_tokens(tokens)
		updated, ignored = superglot.update_user_words(user, words, 3)
		common_words = list(superglot.get_common_words(user, article))
		common_lemmata = list(map(lambda w: w[0].word.lemma, common_words))
		common_set = set(common_lemmata)
		
		eq_(len(common_lemmata), len(common_set))
		eq_(updated, len(common_words))
