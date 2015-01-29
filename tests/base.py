from nose.tools import *
import io
import os
from unittest import mock
import requests
from flask import url_for
from flask.ext.sqlalchemy import SQLAlchemy

from superglot import nlp
from superglot import util
from superglot import models
from superglot import core

from datetime import datetime, timedelta

from flask.ext.testing import TestCase


class SuperglotTestBase(TestCase):

    app = None
    client = None

    account_fixtures = [{'email': "%04i@test.com" % i, 'password': "test%04i" % i} for i in range(1, 4)]

    test_articles = [
        {
            'file': 'data/articles/game-for-fools.txt',
            'title': 'The Game For Fools',
            'num_sentences': 1,
            'num_words': 197,
        },
        {
            'file': 'data/articles/little-prince-1.txt',
            'title': 'The Little Prince Ch. 1',
            'num_sentences': 34,
            'num_words': 999,
        },
        {
            'file': 'data/articles/little-prince-2.txt',
            'title': 'The Little Prince Ch. 2',
            'num_sentences': 61,
            'num_words': 999,
        },
    ]

    def _create_article(self, user, article_def):
        with open(article_def['file'], 'r') as f:
            plaintext = f.read()
            article, created = core.create_article(
                user=user,
                title=article_def['title'],
                plaintext=plaintext[0:]
            )
        return article, created

    def make_url(self, uri):
        base = 'http://localhost:31338/'
        return base + uri

    def post(self, uri, data={}, follow_redirects=True):
        return self.client.post(self.make_url(uri), data=data, follow_redirects=follow_redirects)

    def create_app(self):
        import superglot
        return superglot.create_app()

    def get_user(self):
        return models.User.query().first()

    def setUp(self):
        self._add_accounts()

    def tearDown(self):
        # delete everything other than Word
        self.db.session.query(models.User).delete()
        self.db.session.query(models.VocabWord).delete()
        self.db.session.query(models.WordOccurrence).delete()
        self.db.session.query(models.Article).delete()
        self.db.session.commit()

        # qs = get_debug_queries()
        # print(qs)

    @classmethod
    def _add_accounts(cls):
        for account in cls.account_fixtures:
            user, created = core.register_user(email=account['email'], password=account['password'])
            assert user
            assert created

    @classmethod
    def setup_class(cls):
        from superglot import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.db = cls.app.db

    @classmethod
    def teardown_class(cls):
        cls.db.session.close()