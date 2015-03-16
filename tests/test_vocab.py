from nose import tools as nt

from superglot import (
    core,
    models,
    nlp,
)

from .base import SuperglotTestBase


class TestVocab(SuperglotTestBase):

    def test_vocab_search(self):
        user = self.get_user()
        tokens = nlp.tokenize('apple banana mushroom')
        words = core.gen_words_from_tokens(tokens)

        core.update_user_words(user, words, 2)

        vocab = core.user_vocab_search(user, 'a')

        nt.assert_equals(vocab.count(), 1)
