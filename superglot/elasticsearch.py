
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch_dsl import Search

from config import settings

from pprint import pprint


def _drop(es):
	"""drops the Elasticsearch index"""
	try:
		es.indices.delete(index=settings.ES_INDEX)
	except NotFoundError:
		print("No index to drop named: %s" % settings.ES_INDEX)


def _create(es):
	"""sets up Elasticsearch index and mappings"""
	es.indices.create(index=settings.ES_INDEX, ignore=400)

	for doc_type in ('article', 'user'):
		mapping_dict = _create_mapping_dict(doc_type)
		es.indices.put_mapping(
			index=settings.ES_INDEX,
			doc_type=doc_type,
			body=mapping_dict
		)


def _create_mapping_dict(doc_type):

	if doc_type == 'article':
		mapping_dict = {
			'article': {
				'date_detection': True,
				'numeric_detection': False,
				'properties': {
					'title': {
						'type': 'string'
					},
					'plaintext': {
						'type': 'string',
						'analyzer': 'english',
					},
				}
			}
		}
	elif doc_type == 'user':
		mapping_dict = {
			'user': {
				'date_detection': True,
				'numeric_detection': True,
				'properties': {

				}
			}
		}
	else:
		mapping_dict = {
			doc_type: {}
		}

	return mapping_dict


def _populate_index(es):

	from superglot import models
	from superglot import util
	from elasticsearch.helpers import bulk

	def serialize_model(row):
		return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())

	def serialize_user(user):
		json = serialize_model(user)
		vocabdict = util.dict_from_seq(user.vocab, lambda v: v.word.lemma)
		for k in vocabdict:
			vocabdict[k] = serialize_model(vocabdict[k])
			del vocabdict[k]['user_id']
		json['vocab'] = vocabdict
		del json['password']
		return json

	def add_stuff(doc_type, coll):
		print(doc_type)
		pprint( bulk(
			es,
			coll,
			index=settings.ES_INDEX,
			doc_type=doc_type,
		))

	add_stuff('user', map(serialize_user, models.User.query().all()))
	add_stuff('article', map(serialize_model, models.Article.query().all()))
	# add_stuff('word', map(serialize_model, models.Word.query().all()))


def get_client():
	"""returns an Elasticsearch inst. with project settings"""
	# return Elasticsearch([{'host': settings.ES_HOST}])
	return Elasticsearch()


def rebuild_index(es):
	_drop(es)
	_create(es)
	_populate_index(es)


def search_query(es, doc_type):
	"""returns instance of elasticsearch_dsl Search inst."""
	return Search(
		using=es,
		index=settings.ES_INDEX,
		doc_type=doc_type,
	)
