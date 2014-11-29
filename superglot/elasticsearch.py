
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from config import settings


def elasticsearch_client():
    """returns an Elasticsearch inst. with project settings"""
    # return Elasticsearch([{'host': settings.ES_HOST}])
    return Elasticsearch()


def es_search_query(es, doc_type):
    """returns instance of elasticsearch_dsl Search inst."""
    return Search(
        using=es,
        index=settings.ES_INDEX,
        doc_type=doc_type,
    )
