import os

from elasticsearch import Elasticsearch


def get_es_client() -> Elasticsearch:
    return Elasticsearch(
        hosts=[os.environ["ES_HOST"]],
        basic_auth=(os.environ["ES_USER"], os.environ["ES_PASSWORD"]),
        ca_certs=os.environ.get("ES_CA_CERT"),
    )
