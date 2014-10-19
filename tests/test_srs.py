from nose.tools import *
import io
import os
from unittest import mock
from datetime import datetime, timedelta

import requests
from flask import url_for

import models
import nlp
import util
from config import settings
import superglot

from .base import SuperglotTestBase


class TestSRS(SuperglotTestBase):

	lemmata_fixture = ['']

	def test(self):
			user = self.db.session.query(models.User).first()
			words = self.db.session.query(models.Word)
			ignored_words = words[0:20]
			wordsets = {
				1: words[20:40],
				2: words[20:40],
				3: words[40:60],
				4: words[60:80],
			}

			# TODO: once the SRS scheme is solidified, simulate a bunch of updates over days and months and see if they make sense
			intervals = [
				{

				}
			]

			superglot.update_user_words(user, ignored_words, settings.RATING_NAMES['ignored'])

			for score, words in wordsets.items():
				num = superglot.update_user_words(user, words, score)

			with mock.patch('util.now'):
				util.now.return_value = datetime.now() + timedelta(days=1)
				for score, words in wordsets.items():
					num = superglot.update_user_words(user, words, score)
					
