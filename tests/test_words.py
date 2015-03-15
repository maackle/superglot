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
        updated = core.update_user_words(user, words, 3)
        common_words = list(core.get_common_vocab(user, article))
        common_lemmata_set = {w.word.lemma for w in common_words}

        nt.eq_(len(common_words), len(common_lemmata_set))
        nt.assert_set_equal(set(common_words), set(updated))

    def test_generate_words(self):
        words1 = core.gen_words_from_tokens(
            nlp.tokenize("Running watery noses")
        )
        words2 = core.gen_words_from_tokens(
            nlp.tokenize("Running faucets are the coolest")
        )

        for words in (words1, words2):
            nt.assert_true(all(w.id for w in words))

        nt.assert_equal(
            ("run watery nose".split(' ')),
            [w.lemma for w in words1],
        )

        nt.assert_equal(
            ("run faucet be the cool".split(' ')),
            [w.lemma for w in words2],
        )

    def test_generate_words_w_punctuation(self):

        words = core.gen_words_from_tokens(
            nlp.tokenize('''
                "He's on his way", said _mushmouth_ the dog. "Oh well!
                There goes...the day."
            ''')
        )

        nt.assert_equal(
            [w.lemma for w in words if w.id],
            [
                'he', "'s", 'on', 'his', 'way', 'say', '_mushmouth_', 'the',
                'dog.', 'oh', 'well', 'there', 'go', 'the', 'day.'
            ]
        )

        nt.assert_equal(
            [w.lemma for w in words if not w.id],
            [
                '"', '"', ',', '"', '!', '...', '"',
            ]
        )

    def test_lengths(self):
        plaintext = """
        How do you do? I've got...twenty-five head of cow here, d'ya wanna
        buy? Whaddya say?
        """
        tokens = nlp.tokenize(plaintext)
        spans = nlp.span_tokenize(plaintext)
        words = core.gen_words_from_tokens(tokens)

        l = len(words)
        nt.assert_true(len(tokens), l)
        nt.assert_true(len(spans), l)

    def test_generate_words_readings(self):
        core.gen_words_from_tokens(
            nlp.tokenize("Running watery noses")
        )
        core.gen_words_from_tokens(
            nlp.tokenize("Running faucets are the coolest")
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
            {(x.lemma, x.reading) for x in models.LemmaReading.query}
        )
