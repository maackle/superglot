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
from database import db

from .base import SuperglotTestBase


class TestMisc(SuperglotTestBase):

	def test_url(self):
		with self.app.test_request_context():
			eq_(url_for('auth.register'), '/auth/register/')
			eq_(url_for('auth.login'), '/auth/login/')
			eq_(url_for('study.words'), '/study/words/')