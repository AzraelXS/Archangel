"""
Thin ES-index-backed model helpers. The project deliberately has no RDBMS
for application data (see archangel.settings) -- tenant/collector records
live in Elasticsearch, same as everything else, via dashboard.es_client.
"""
import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from elasticsearch import NotFoundError

from dashboard.es_client import get_es_client

TENANTS_INDEX = "archangel-tenants"
COLLECTORS_INDEX = "archangel-collectors"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def create_tenant(name: str) -> dict:
    """Creates a tenant and returns the record including the one-time raw API key."""
    es = get_es_client()
    tenant_id = str(uuid.uuid4())
    raw_key = secrets.token_urlsafe(32)
    doc = {
        "tenant_id": tenant_id,
        "name": name,
        "api_key_hash": hash_api_key(raw_key),
        "created_at": _now(),
    }
    es.index(index=TENANTS_INDEX, id=tenant_id, document=doc, refresh="wait_for")
    return {**doc, "api_key": raw_key}


def get_tenant_by_api_key(raw_key: str) -> dict | None:
    es = get_es_client()
    key_hash = hash_api_key(raw_key)
    result = es.search(
        index=TENANTS_INDEX,
        query={"term": {"api_key_hash": key_hash}},
        size=1,
        ignore_unavailable=True,
    )
    hits = result["hits"]["hits"]
    return hits[0]["_source"] if hits else None


def _collector_id_for(tenant_id: str, name: str) -> str:
    """Deterministic id so concurrent registrations of the same (tenant_id, name)
    always upsert the same document instead of racing on a search-then-create."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"archangel-collector:{tenant_id}:{name}"))


def register_collector(tenant_id: str, name: str) -> dict:
    """
    Idempotent on (tenant_id, name) by construction: the doc _id is derived
    from those fields, so any number of concurrent callers upsert the same
    document rather than racing a search-then-create and creating
    duplicates.
    """
    es = get_es_client()
    collector_id = _collector_id_for(tenant_id, name)
    now = _now()
    try:
        existing = es.get(index=COLLECTORS_INDEX, id=collector_id)
        registered_at = existing["_source"]["registered_at"]
    except NotFoundError:
        registered_at = now

    doc = {
        "collector_id": collector_id,
        "tenant_id": tenant_id,
        "name": name,
        "status": "online",
        "registered_at": registered_at,
        "last_seen": now,
    }
    es.index(index=COLLECTORS_INDEX, id=collector_id, document=doc, refresh="wait_for")
    return doc


def touch_collector(collector_id: str) -> None:
    es = get_es_client()
    es.update(index=COLLECTORS_INDEX, id=collector_id, doc={"last_seen": _now(), "status": "online"})
