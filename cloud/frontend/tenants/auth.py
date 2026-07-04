from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .es_index import get_tenant_by_api_key


class TenantApiKeyUser:
    """Lightweight stand-in for a Django user, carrying the resolved tenant."""

    is_authenticated = True

    def __init__(self, tenant: dict):
        self.tenant = tenant
        self.tenant_id = tenant["tenant_id"]


class TenantApiKeyAuthentication(BaseAuthentication):
    """Authenticates collector requests via `Authorization: Bearer <tenant_api_key>`."""

    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None

        raw_key = header.removeprefix("Bearer ").strip()
        tenant = get_tenant_by_api_key(raw_key)
        if tenant is None:
            raise AuthenticationFailed("Invalid tenant API key")

        return (TenantApiKeyUser(tenant), None)
