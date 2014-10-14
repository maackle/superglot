from nose.tools import *
import io
import os
from unittest import mock
from datetime import datetime, timedelta

import requests
from flask import url_for

from relational import models
import nlp
import util
from config import settings
import database as db

from .base import SuperglotTestBase


class TestSRS(SuperglotTestBase):

	lemmata_fixture = ['']

	def test(self):
		with db.session() as session:
			user = session.query(models.User).first()
			words = session.query(models.Word)
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

			user.update_words(ignored_words, settings['SCORES']['ignored'])

			for score, words in wordsets.items():
				num = user.update_words(words, score)

			with mock.patch('util.now'):
				util.now.return_value = datetime.now() + timedelta(days=1)
				for score, words in wordsets.items():
					num = user.update_words(words, score)
					
