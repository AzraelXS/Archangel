from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from tenants.es_index import list_collectors, list_tenants

from .es_client import get_es_client


def health(request):
    es = get_es_client()
    return JsonResponse({
        "tenant_id": request.tenant_id,
        "elasticsearch": es.ping(),
    })


@login_required
def tenants_view(request):
    tenants = list_tenants()
    collectors = list_collectors()
    collectors_by_tenant = {}
    for collector in collectors:
        collectors_by_tenant.setdefault(collector["tenant_id"], []).append(collector)

    for tenant in tenants:
        tenant["collectors"] = collectors_by_tenant.get(tenant["tenant_id"], [])

    return render(request, "dashboard/tenants.html", {"tenants": tenants})
