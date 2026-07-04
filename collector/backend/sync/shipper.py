import logging
import os

import requests

from core.es_client import get_es_client
from sync.client import get_cached_collector_id

log = logging.getLogger("sync-shipper")

LOCAL_EVENTS_INDEX = "collector-events-*"
BATCH_SIZE = 200


def ship_backlog():
    """
    Queries local ES for records not yet shipped, pushes them to the cloud
    ingest endpoint in a batch, and marks each shipped only once the cloud
    side has accepted it -- records that fail to ship simply stay
    shipped=false and get retried on the next run, so nothing is dropped
    on a failed push or a WAN outage.
    """
    collector_id = get_cached_collector_id()
    if collector_id is None:
        log.info("not yet registered with cloud, skipping this cycle")
        return

    es = get_es_client()
    cloud_api_url = os.environ["CLOUD_API_URL"].rstrip("/")
    api_key = os.environ["TENANT_API_KEY"]

    result = es.search(
        index=LOCAL_EVENTS_INDEX,
        query={"term": {"shipped": False}},
        size=BATCH_SIZE,
    )
    hits = result["hits"]["hits"]
    if not hits:
        return

    records = [hit["_source"] for hit in hits]
    try:
        resp = requests.post(
            f"{cloud_api_url}/collectors/{collector_id}/ingest",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"records": records},
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.warning("shipping failed, will retry next cycle: %s", exc)
        return

    for hit in hits:
        es.update(index=hit["_index"], id=hit["_id"], doc={"shipped": True})
    log.info("shipped %d records to cloud", len(hits))
