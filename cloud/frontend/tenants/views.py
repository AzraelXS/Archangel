from datetime import datetime, timezone

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from dashboard.es_client import get_es_client

from .auth import TenantApiKeyAuthentication
from .es_index import get_tenant_by_api_key, register_collector, touch_collector


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def register_collector_view(request):
    """
    A collector presents its tenant API key + a self-chosen name and gets
    back a collector_id. Idempotent on (tenant, name) so restarts don't
    create duplicate collector rows.
    """
    raw_key = request.data.get("api_key")
    name = request.data.get("name")
    if not raw_key or not name:
        return Response({"error": "api_key and name are required"}, status=400)

    tenant = get_tenant_by_api_key(raw_key)
    if tenant is None:
        return Response({"error": "invalid api_key"}, status=401)

    collector = register_collector(tenant_id=tenant["tenant_id"], name=name)
    return Response({"collector_id": collector["collector_id"], "tenant_id": tenant["tenant_id"]})


@api_view(["POST"])
@authentication_classes([TenantApiKeyAuthentication])
@permission_classes([IsAuthenticated])
def ingest_view(request, collector_id):
    """
    Accepts a batch of normalized records (see common.events.NormalizedRecord)
    from an authenticated collector and writes them into this tenant's
    event/metric indices.
    """
    tenant_id = request.user.tenant_id
    records = request.data.get("records", [])
    if not isinstance(records, list) or not records:
        return Response({"error": "records must be a non-empty list"}, status=400)

    es = get_es_client()
    now = datetime.now(timezone.utc).isoformat()
    for record in records:
        kind = record.get("kind", "event")
        index = f"tenant-{tenant_id}-{kind}s-{now[:7]}"  # e.g. tenant-<id>-events-2026-07
        es.index(
            index=index,
            document={
                **record,
                "tenant_id": tenant_id,
                "collector_id": collector_id,
                "ingested_at": now,
            },
        )

    touch_collector(collector_id)
    return Response({"accepted": len(records)})
