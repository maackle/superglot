from nose.tools import *

from flask import url_for

from superglot import models
from superglot import core

from .base import SuperglotTestBase
from superglot import core


class TestAuth(SuperglotTestBase):

    test_account = {'email': 'test@superglot.com', 'password': '1234'}

    def test_register(self):
        user, created = core.register_user("axabras@gmail.com", "axabras")
        assert user
        assert_true(created)

    def test_register_route(self):
        assert not self.db.session.query(models.User).filter_by(email=self.test_account['email']).first()
        r = self.post(url_for('auth.register'), data={
            'email': self.test_account['email'],
            'password': self.test_account['password'],
        })
        user = self.db.session.query(models.User).filter_by(email=self.test_account['email']).first()
        assert user
        eq_(r.status_code, 200)

    def test_login(self):
        r = self.post(url_for('auth.login'), data={
            'email': self.account_fixtures[0]['email'],
            'password': self.account_fixtures[0]['password'],
        })
        eq_(r.status_code, 200)

    def test_url(self):
        with self.app.test_request_context():
            eq_(url_for('auth.register'), '/auth/register/')
            eq_(url_for('auth.login'), '/auth/login/')
            eq_(url_for('study.words'), '/study/words/')

