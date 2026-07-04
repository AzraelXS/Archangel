from django.http import JsonResponse

from .es_client import get_es_client


def health(request):
    es = get_es_client()
    return JsonResponse({
        "tenant_id": request.tenant_id,
        "elasticsearch": es.ping(),
    })
