from nose.tools import *
import io
import os
from unittest import mock
import requests

from flask import url_for
from datetime import datetime, timedelta

from application import create_app
from relational import models
import nlp
import util

from .base import SuperglotTestBase


class TestArticle(SuperglotTestBase):
	
	test_account = {'email': 'test@superglot.com', 'password': '1234'}

	def test_create_article(self):
		with self.app.test_request_context():
			import superglot
			from database import db
			from relational import models
			user = db.session.query(models.User).first()
			
			with open('data/articles/moby-dick-full.txt', 'r') as f:
				plaintext = f.read()
				article = superglot.create_article(user=user, title="Moby Dick", plaintext=plaintext[0:])
				print(article.sentence_positions)
