from nose.tools import *
import io
import os
from unittest import mock
import requests

from application import create_app
import models
import nlp
import util

from flask import url_for
from datetime import datetime, timedelta


class SuperglotTestBase(object):

	app = None
	client = None

	account_fixtures = [{'email': "%04i@test.com" % i, 'password': "test%04i" % i} for i in range(1, 4)]

	def make_url(self, uri):
		base = 'http://localhost:31338/'
		return base + uri

	def post(self, uri, data={}, follow_redirects=True):
		return self.client.post(self.make_url(uri), data=data, follow_redirects=follow_redirects)

	@classmethod
	def _add_accounts(cls):
		for account in cls.account_fixtures:
			user, created = models.User.register(email=account['email'], password=account['password'])
			assert user
			assert created

	# @classmethod
	# def _add_words(cls):
	# 	with open('tests/fixtures/initial-words.txt', 'r') as infile:
	# 		def gen():
	# 			for line in infile:
	# 				reading = line.strip()
	# 				# yield models.Word(reading=reading, lemma=nlp.lemmatize_word(reading), language='en')
	# 				yield {
	# 					"reading": reading, "lemma": nlp.lemmatize_word(reading), "language": 'en',
	# 				}
	# 		models.Word.objects.insert(gen())
	# 		num = models.Word.objects.count()
	# 		cls.app.logger.info("{} words added".format(num))

	# @classmethod
	# def _teardown_db(cls):
	# 	from mongoengine import connect
	# 	from config import testing as config
	# 	db_name = config.MONGODB_SETTINGS['DB']
	# 	assert db_name == 'superglot_test'
	# 	db = connect(db_name)
	# 	db.drop_database(db_name)

	@classmethod
	def setup_class(cls):
		os.environ["SUPERGLOT_SETTINGS"] = 'config/testing.py'
		cls.app = create_app()
		cls.client = cls.app.test_client()

		with cls.app.app_context():
			cls._add_accounts()
			# cls._add_words()

	@classmethod
	def teardown_class(cls):
		models.User.drop_collection()


class TestAuth(SuperglotTestBase):

	test_account = {'email': 'test@superglot.com', 'password': '1234'}

	# @classmethod
	# def setup_class(cls):
	# 	super().setup_class()

	def test_register(self):
		with self.app.test_request_context():
			assert not models.User.objects(email=self.test_account['email']).first()
			r = self.post(url_for('auth.register'), data={
				'email': self.test_account['email'],
				'password': self.test_account['password'],
			})
			user = models.User.objects(email=self.test_account['email']).first()
			assert r.status_code is 200
			assert user

	def test_login(self):
		with self.app.test_request_context():
			# import pdb; pdb.set_trace()
			r = self.post(url_for('auth.login'), data={
				'email': self.account_fixtures[0]['email'],
				'password': self.account_fixtures[0]['password'],
			})
			assert r.status_code is 200

	def test_url(self):
		with self.app.test_request_context():
			eq_(url_for('auth.register'), '/auth/register/')
			eq_(url_for('auth.login'), '/auth/login/')
			eq_(url_for('study.words'), '/study/words/')


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

			user.update_words(ignored_words, self.app.config['SCORES']['ignored'])

			for score, words in wordsets.items():
				num = user.update_words(words, score)
				print(num)

			with mock.patch('util.now'):
				util.now.return_value = datetime.now() + timedelta(days=1)
				for score, words in wordsets.items():
					num = user.update_words(words, score)
					print(num)
