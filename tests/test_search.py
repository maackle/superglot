from nose.tools import *

from superglot import models
from superglot import core
from superglot import elasticsearch as es

from sqlalchemy.sql.expression import func
from .base import SuperglotTestBase

from pprint import pprint

class TestSearch(SuperglotTestBase):

	def test_search(self):

		user = self.get_user()

		for article_def in self.test_articles:
			self._create_article(user, article_def)
		es.rebuild_index(self.app.es)

		vocab_string = " ".join([w.word.lemma for w in user.vocab])
		lemmata = (w.word.lemma for w in user.vocab)
		shoulds = [{'match': {'plaintext': l}} for l in lemmata]

		results = self.app.es.search('superglot_test', 'article', {
			'query': {
				'bool': {
					'should': shoulds
				}
			}
		}, size=100000)

		hits = results['hits']['hits']

		print("# hits: ", len(hits))


		# results = s.execute()
		# pprint(results.hits)