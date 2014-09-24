from nose.tools import *
import io
import os
import requests

from application import create_app
import models

from flask import url_for


class SuperglotTestBase(object):

	app = None
	client = None

	def make_url(self, uri):
		base = 'http://localhost:31338/'
		return base + uri

	def post(self, uri, data={}, follow_redirects=True):
		self.client.post(self.make_url(uri), data={
			'email': '0001@test.com',
			'password': 'test0001',
		}, follow_redirects=follow_redirects)


	@classmethod
	def setup_class(cls):
		os.environ["SUPERGLOT_SETTINGS"] = 'config.testing'
		cls.app = create_app()
		cls.client = cls.app.test_client()


class TestReport(SuperglotTestBase):

	def test_register(self):
		r = self.post('auth/register/', data={
			'email': '0001@test.com',
			'password': 'test0001',
		})

	def test_url(self):
		with self.app.test_request_context('/'):
			eq_(url_for('auth.register'), '/auth/register/')
			eq_(url_for('auth.login'), '/auth/login/')