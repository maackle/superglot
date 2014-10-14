from nose.tools import *
import io
import os
from unittest import mock
import requests

from flask import url_for
from datetime import datetime, timedelta

from relational import models
import nlp
import util

from .base import SuperglotTestBase


class TestAuth(SuperglotTestBase):

	test_account = {'email': 'test@superglot.com', 'password': '1234'}

	# @classmethod
	# def setup_class(cls):
	# 	super().setup_class()

	def test_register(self):
		with self.app.test_request_context():
			user, created = superglot.register_user("axabras@gmail.com", "axabras")
			assert user
			assert created

	def test_register_route(self):
		with self.app.test_request_context():
			assert not self.db.session.query(models.User).filter(email=self.test_account['email']).first()
			r = self.post(url_for('auth.register'), data={
				'email': self.test_account['email'],
				'password': self.test_account['password'],
			})
			user = self.db.session.query(models.User).filter(email=self.test_account['email']).first()
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

