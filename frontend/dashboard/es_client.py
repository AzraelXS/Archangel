from functools import lru_cache

from django.conf import settings
from elasticsearch import Elasticsearch


@lru_cache
def get_es_client() -> Elasticsearch:
    cfg = settings.ELASTICSEARCH
    return Elasticsearch(
        hosts=[cfg["HOST"]],
        basic_auth=(cfg["USER"], cfg["PASSWORD"]),
        ca_certs=cfg["CA_CERT"],
    )
