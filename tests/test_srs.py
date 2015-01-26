from nose.tools import *
import io
import os
from unittest import mock
from datetime import datetime, timedelta

import requests
from flask import url_for

from superglot import models
from superglot import nlp
from superglot import util
from superglot.config import settings
from superglot import core

from .base from superglot import coreTestBase


class TestSRS(SuperglotTestBase):

	lemmata_fixture = ['']

	def _add_sample_vocab_words(self, user):
		words = models.query(models.Word)
		wordsets = {
			settings.RATING_VALUES['ignored']: set(words[0:20]),
			1: set(words[20:40]),
			2: set(words[40:60]),
			3: set(words[60:80]),
			4: set(words[80:100]),
		}
		for score, words in wordsets.items():
		 core.update_user_words(user, words, score)
		return wordsets


	def test_due(self):
		user = self.get_user()
		wordsets = self._add_sample_vocab_words(user)
		due_vocab = core.gen_due_vocab(user)


	def test_intervals(self):
		user = self.get_user()

		wordsets = self._add_sample_vocab_words(user)

		# TODO: once the SRS scheme is solidified, simulate a bunch of updates over days and months and see if they make sense
		intervals = [
			{

			}
		]

		with mock.patch('util.now'):
			util.now.return_value = datetime.now() + timedelta(days=1)
			for score, words in wordsets.items():
			 core.update_user_words(user, words, score)

