from nose.tools import *
import io
import os
from unittest import mock
from datetime import datetime, timedelta

import requests
from flask import url_for

from application import create_app
import models
import nlp
import util

from .base import SuperglotTestBase


class TestSRS(SuperglotTestBase):

	lemmata_fixture = ['']

	def test(self):
		with self.app.app_context():
			user = models.User.objects.first()
			ignored_words = models.Word.objects[0:20]
			wordsets = {
				1: models.Word.objects[20:40],
				2: models.Word.objects[20:40],
				3: models.Word.objects[40:60],
				4: models.Word.objects[60:80],
			}

			# TODO: once the SRS scheme is solidified, simulate a bunch of updates over days and months and see if they make sense
			intervals = [
				{

				}
			]

			user.update_words(ignored_words, self.app.config['SCORES']['ignored'])

			for score, words in wordsets.items():
				num = user.update_words(words, score)

			with mock.patch('util.now'):
				util.now.return_value = datetime.now() + timedelta(days=1)
				for score, words in wordsets.items():
					num = user.update_words(words, score)
					
