from nose.tools import *
import io
import os
from unittest import mock
import requests

from flask import url_for
from datetime import datetime, timedelta

from superglot import models
from superglot import nlp
from superglot import util

from .base import SuperglotTestBase
from superglot import core


class TestMisc(SuperglotTestBase):

    def test_url(self):
        with self.app.test_request_context():
            eq_(url_for('auth.register'), '/auth/register/')
            eq_(url_for('auth.login'), '/auth/login/')
            eq_(url_for('study.words'), '/study/words/')

    # def test_page_renders(self):
    #   for endpoint, rule in util.get_site_links(self.app):
    #       r = requests.get('http:/'+endpoint)
    #       eq_(r, 200)