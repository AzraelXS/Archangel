"""
Resolves the active tenant for each request and stashes it on request.tenant_id.
Placeholder: reads an X-Tenant-Id header until real tenant/org auth exists.
All Elasticsearch queries downstream must filter on request.tenant_id to
keep customer data isolated within shared indices.
"""


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant_id = request.headers.get("X-Tenant-Id", "default")
        return self.get_response(request)
