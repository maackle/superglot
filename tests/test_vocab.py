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

        core.vocab_search(user)