import os
from elasticsearch import Elasticsearch


def init_es():
    ES_HOST = os.environ.get('ES_HOST', 'localhost')
    ES_PORT = os.environ.get('ES_PORT', '9200')
    ES_USER = os.environ.get('ES_USER', 'elastic')
    ES_PASS = os.environ.get('ES_PASS', 'changeme')

    return Elasticsearch(
        [{'host': ES_HOST, 'port': ES_PORT}],
        http_auth=(ES_USER, ES_PASS),
        http_compress=True
    )


es = init_es()
