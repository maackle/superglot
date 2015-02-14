from nose import tools as nt

from superglot import (
    core,
    models,
    nlp,
)

from .base import SuperglotTestBase


class TestWords(SuperglotTestBase):

    def test_common_words(self):

        user = self.db.session.query(models.User).first()
        article_def = self.test_articles[0]

        with open(article_def['file'], 'r') as f:
            plaintext = f.read()
            article, created = core.create_article(user=user, title=article_def['title'], plaintext=plaintext)

        tokens = nlp.tokenize(plaintext)
        words = core.gen_words_from_tokens(tokens)
        updated, ignored = core.update_user_words(user, words, 3)
        common_words = list(core.get_common_vocab(user, article))
        common_lemmata = list(map(lambda w: w.word.lemma, common_words))
        common_set = set(common_lemmata)

        nt.eq_(len(common_lemmata), len(common_set))
        nt.eq_(updated, len(common_words))

    def test_generate_words(self):
        words1 = list(core.gen_words_from_readings(
            "Running watery noses".split(' '))
        )
        words2 = list(core.gen_words_from_readings(
            "Running faucets are the coolest".split(' '))
        )
        for words in (words1, words2):
            nt.assert_true(all(w.id for w in words))

        nt.assert_equal(
            ("running watery nose noses".split(' ')),
            [w.lemma for w in words1],
        )

        nt.assert_equal(
            ("running faucet faucets are be the cool coolest".split(' ')),
            [w.lemma for w in words2],
        )

    def test_generate_words_readings(self):
        words1 = list(core.gen_words_from_readings(
            "Running watery noses".split(' '))
        )
        words2 = list(core.gen_words_from_readings(
            "Running faucets are the coolest".split(' '))
        )

        nt.assert_set_equal(
            set([
                ('the', 'the'),
                ('are', 'are'),
                ('noses', 'noses'),
                ('faucets', 'faucets'),
                ('nose', 'noses'),
                ('running', 'Running'),
                ('faucet', 'faucets'),
                ('coolest', 'coolest'),
                ('cool', 'coolest'),
                ('watery', 'watery'),
                ('be', 'are'),
            ]),
            {(x.lemma, x.reading) for x in models.LemmaReading.query()}
        )