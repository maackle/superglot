from nose import tools as nt

from superglot import (
    core,
    models,
    nlp,
)

from .base import SuperglotTestBase


class TestNLP(SuperglotTestBase):

    def test_tokenize(self):
        tokens = nlp.tokenize("Children are happiest when drumming")
        nt.assert_equal(
            [tok.lemma for tok in tokens],
            'child be happy when drum'.split(' ')
        )

    def test_tokenize_length(self):
        '''
        Check that readings map to words one to one
        '''
        tokens = nlp.tokenize("To be or not to be is the question")

        nt.assert_equal(len(tokens), 9)
        nt.assert_equal(
            {tok.lemma for tok in tokens},
            {'be', 'to', 'or', 'not', 'the', 'question'}
        )
