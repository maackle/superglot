from nose.tools import *

from superglot import models
from superglot import core
from superglot import elasticsearch as es

from sqlalchemy.sql.expression import func
from .base import SuperglotTestBase

from pprint import pprint

class TestAuth(SuperglotTestBase):

	def test_search(self):

		user = self.get_user()

		for article_def in self.test_articles:
			self._create_article(user, article_def)
		es.rebuild_index(self.app.es)

		vocab_string = " ".join(list(map(lambda w: w.word.lemma, user.vocab)))

		lemmata = list(map(lambda w: w.word.lemma, user.vocab))
		shoulds = list(map(lambda l: {'match': {'plaintext': l}}, lemmata))

		# s = (
		# 	es.search_query(self.app.es, 'article')
		# 	.query('match', plaintext=vocab_string)
		# )

		results = self.app.es.search('superglot_test', 'article', {
			'query': {
				'bool': {
					'should': shoulds
				}
			}
		})

		for r in results['hits']['hits']:
			pprint(r)


		# results = s.execute()
		# pprint(results.hits)