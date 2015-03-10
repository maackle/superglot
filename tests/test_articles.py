import mock

from flask import url_for
from nose import tools as nt

from superglot import models
from superglot import core

from .base import SuperglotTestBase


def _url_mock(text):
    m = mock.MagicMock
    m.text = text
    return m


class TestArticles(SuperglotTestBase):

    test_account = {'email': 'test@superglot.com', 'password': '1234'}

    def test_create_article(self):

        user = self.get_user()

        for article_def in self.test_articles:
            article = self._create_article(user, article_def)
            nt.assert_equal(
                len(article.sentence_positions.keys()),
                article_def['num_sentences']
            )

    @mock.patch('superglot.util.get_url')
    def test_create_article_from_url(self, mocked):
        mocked.side_effect = _url_mock(
            '''
                <head>
                    <title>mythical creatures</title>
                    cute panda
                </head>
                <body>
                    stinky baboon
                </body>
            '''
        )
        self.login(**self.account_creds[0])
        self.client.post(
            url_for('frontend.articles.article_create'),
            data={
                'url': 'http://example.com',
                'plaintext': None,
            }, follow_redirects=True
        )
        article = models.Article.query.first()
        nt.assert_equal(article.title, 'mythical creatures')
        nt.assert_equal(article.plaintext, 'stinky baboon')

    def test_article_occurrences(self):
        user = self.get_user()
        article, created = core.create_article(
            user, "Test 1", "Twelve little toes"
        )
        occurrences = article.word_occurrences
        nt.assert_equal(len(occurrences), 3)
        nt.assert_equal(
            [o.article_position for o in occurrences],
            [0, 7, 14],
        )

    def test_article_stats(self):

        user = self.get_user()
        article_def = self.test_articles[0]
        article = self._create_article(user, article_def)
        words = models.Word.query.all()
        core.update_user_words(user, words[0:10], 3)
        stats = core.compute_article_stats(user, article)
        nt.assert_equal(stats['counts'][3], 10)

    def test_article_annotate(self):
        user = self.get_user()
        article_def = self.test_articles[0]
        article = self._create_article(user, article_def)
        article_vocab_pairs = core.get_common_vocab_pairs(user, article)

        self.pp(article_vocab_pairs)
        assert(False)


class FutureCases(object):
    def test_create_article_twice(self):

        user = self.db.session.query(models.User).first()

        article_def = self.test_articles[0]
        article, created = self._create_article(user, article_def)
        nt.assert_true(created)
        article, created = self._create_article(user, article_def)
        nt.assert_false(created)