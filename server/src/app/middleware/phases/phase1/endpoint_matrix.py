from dataclasses import dataclass
from functools import lru_cache
import re
from typing import Literal

from server.src.app.middleware.phases.phase1.plan_limits import PlanLimits


@dataclass
class EndpointConfig:
    access: Literal["authenticated", "public", "api_key", "hybrid"]
    rate_by: Literal["ip", "user", "api_key", "hybrid"]
    rate_hits: int = 0
    rate_window: int = 0
    max_body_bytes: int = 1024
    csp: bool = False
    idempotency: bool = False
    plan_limits: dict[str, PlanLimits] | None = None


RouteEntry = tuple[str, str, EndpointConfig]


ROUTE_MATRIX: list[RouteEntry] = [
    ("GET", "/v1/health", EndpointConfig(access="public", rate_by="ip", rate_hits=100, rate_window=60, max_body_bytes=0)),

    # --- OpenAPI Docs (dev only) ---
    ("GET", "/docs", EndpointConfig(access="public", rate_by="ip", rate_hits=100, rate_window=60, max_body_bytes=0)),
    ("GET", "/redoc", EndpointConfig(access="public", rate_by="ip", rate_hits=100, rate_window=60, max_body_bytes=0)),
    ("GET", "/openapi.json", EndpointConfig(access="public", rate_by="ip", rate_hits=100, rate_window=60, max_body_bytes=0)),

    # --- Authentication ---
    ("POST", "/v1/auth/signup/initiate", EndpointConfig(access="public", rate_by="ip", rate_hits=5, rate_window=60, max_body_bytes=512, idempotency=True)),
    ("POST", "/v1/auth/signup/complete", EndpointConfig(access="public", rate_by="ip", rate_hits=7, rate_window=60, max_body_bytes=512, idempotency=True)),
    ("POST", "/v1/auth/login/initiate", EndpointConfig(access="public", rate_by="ip", rate_hits=10, rate_window=60, max_body_bytes=512, idempotency=True)),
    ("POST", "/v1/auth/login/complete", EndpointConfig(access="public", rate_by="ip", rate_hits=7, rate_window=60, max_body_bytes=256, idempotency=True)),
    ("GET", "/v1/auth/user/me", EndpointConfig(access="authenticated", rate_by="ip", rate_hits=100, rate_window=60, max_body_bytes=0, csp=True)),
    ("GET", "/v1/auth/user/profile", EndpointConfig(access="authenticated", rate_by="user", rate_hits=60, rate_window=60, max_body_bytes=0, csp=True)),
    ("GET", "/v1/auth/user/sessions", EndpointConfig(access="authenticated", rate_by="user", rate_hits=60, rate_window=60, max_body_bytes=0, csp=True)),
    ("GET", "/v1/auth/user/devices", EndpointConfig(access="authenticated", rate_by="user", rate_hits=60, rate_window=60, max_body_bytes=0, csp=True)),
    ("POST", "/v1/auth/logout", EndpointConfig(access="authenticated", rate_by="user", rate_hits=10, rate_window=60, max_body_bytes=64, idempotency=True)),
    ("POST", "/v1/auth/email/change/initiate", EndpointConfig(access="authenticated", rate_by="user", rate_hits=3, rate_window=3600, max_body_bytes=512, idempotency=True)),
    ("POST", "/v1/auth/email/change/complete", EndpointConfig(access="authenticated", rate_by="user", rate_hits=5, rate_window=3600, max_body_bytes=128, idempotency=True)),
    ("POST", "/v1/auth/account/delete/initiate", EndpointConfig(access="authenticated", rate_by="user", rate_hits=3, rate_window=3600, max_body_bytes=64, idempotency=True)),
    ("POST", "/v1/auth/account/delete/complete", EndpointConfig(access="authenticated", rate_by="user", rate_hits=5, rate_window=3600, max_body_bytes=128, idempotency=True)),
    ("POST", "/v1/auth/password/change/complete", EndpointConfig(access="authenticated", rate_by="user", rate_hits=7, rate_window=900, max_body_bytes=512, idempotency=True)),
    ("POST", "/v1/auth/password/reset/initiate", EndpointConfig(access="public", rate_by="ip", rate_hits=3, rate_window=900, max_body_bytes=512, idempotency=True)),
    ("POST", "/v1/auth/password/reset/verify", EndpointConfig(access="public", rate_by="ip", rate_hits=7, rate_window=900, max_body_bytes=512)),
    ("POST", "/v1/auth/password/reset/complete", EndpointConfig(access="public", rate_by="ip", rate_hits=7, rate_window=900, max_body_bytes=512, idempotency=True)),
    ("POST", "/v1/auth/otp/resend", EndpointConfig(access="public", rate_by="ip", rate_hits=3, rate_window=300, max_body_bytes=512)),
    ("POST", "/v1/auth/otp/resend/authenticated", EndpointConfig(access="authenticated", rate_by="user", rate_hits=3, rate_window=300, max_body_bytes=64)),
    ("POST", "/v1/auth/devices/delete", EndpointConfig(access="authenticated", rate_by="user", rate_hits=5, rate_window=60, max_body_bytes=4096, idempotency=True)),
    ("GET", "/v1/auth/oauth/google/initiate", EndpointConfig(access="public", rate_by="ip", rate_hits=10, rate_window=60, max_body_bytes=0)),
    ("POST", "/v1/auth/oauth/google/callback", EndpointConfig(access="public", rate_by="ip", rate_hits=10, rate_window=60, max_body_bytes=1024)),
    ("GET", "/v1/auth/oauth/github/initiate", EndpointConfig(access="public", rate_by="ip", rate_hits=10, rate_window=60, max_body_bytes=0)),
    ("POST", "/v1/auth/oauth/github/callback", EndpointConfig(access="public", rate_by="ip", rate_hits=10, rate_window=60, max_body_bytes=1024)),

    # --- Core Reads ---
    ("GET", "/v1/core/organizations", EndpointConfig(access="authenticated", rate_by="user", rate_hits=60, rate_window=60, max_body_bytes=0, csp=True)),
    ("GET", "/v1/core/organizations/{organization_id}/members", EndpointConfig(access="authenticated", rate_by="user", rate_hits=60, rate_window=60, max_body_bytes=0, csp=True)),
    ("GET", "/v1/core/organizations/{organization_id}/invitations", EndpointConfig(access="authenticated", rate_by="user", rate_hits=60, rate_window=60, max_body_bytes=0, csp=True)),
    ("GET", "/v1/core/organizations/{organization_id}/projects", EndpointConfig(access="authenticated", rate_by="user", rate_hits=60, rate_window=60, max_body_bytes=0, csp=True)),
    ("GET", "/v1/core/organizations/{organization_id}/projects/{project_id}/api-keys", EndpointConfig(access="authenticated", rate_by="user", rate_hits=60, rate_window=60, max_body_bytes=0, csp=True)),
    ("GET", "/v1/core/organizations/{organization_id}/billing", EndpointConfig(access="authenticated", rate_by="user", rate_hits=60, rate_window=60, max_body_bytes=0, csp=True)),

    # --- Core Writes ---
    ("POST", "/v1/core/organizations", EndpointConfig(access="authenticated", rate_by="user", rate_hits=10, rate_window=3600, max_body_bytes=256, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/edit", EndpointConfig(access="authenticated", rate_by="user", rate_hits=20, rate_window=3600, max_body_bytes=256, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/delete/initiate", EndpointConfig(access="authenticated", rate_by="user", rate_hits=3, rate_window=3600, max_body_bytes=64, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/delete/complete", EndpointConfig(access="authenticated", rate_by="user", rate_hits=5, rate_window=3600, max_body_bytes=128, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/delete/resend", EndpointConfig(access="authenticated", rate_by="user", rate_hits=3, rate_window=300, max_body_bytes=0)),
    ("POST", "/v1/core/organizations/{organization_id}/leave", EndpointConfig(access="authenticated", rate_by="user", rate_hits=10, rate_window=3600, max_body_bytes=0, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/transfer", EndpointConfig(access="authenticated", rate_by="user", rate_hits=5, rate_window=3600, max_body_bytes=256, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/members/{target_user_id}/remove", EndpointConfig(access="authenticated", rate_by="user", rate_hits=30, rate_window=3600, max_body_bytes=0, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/members/{target_user_id}/promote", EndpointConfig(access="authenticated", rate_by="user", rate_hits=20, rate_window=3600, max_body_bytes=0, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/members/{target_user_id}/demote", EndpointConfig(access="authenticated", rate_by="user", rate_hits=20, rate_window=3600, max_body_bytes=0, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/invitations", EndpointConfig(access="authenticated", rate_by="user", rate_hits=20, rate_window=3600, max_body_bytes=512, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/invitations/{invitation_id}/cancel", EndpointConfig(access="authenticated", rate_by="user", rate_hits=20, rate_window=3600, max_body_bytes=0, idempotency=True)),
    ("POST", "/v1/core/organizations/invitations/accept", EndpointConfig(access="authenticated", rate_by="user", rate_hits=20, rate_window=3600, max_body_bytes=256, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/projects", EndpointConfig(access="authenticated", rate_by="user", rate_hits=10, rate_window=3600, max_body_bytes=256, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/projects/{project_id}/edit", EndpointConfig(access="authenticated", rate_by="user", rate_hits=20, rate_window=3600, max_body_bytes=256, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/projects/{project_id}/delete", EndpointConfig(access="authenticated", rate_by="user", rate_hits=5, rate_window=3600, max_body_bytes=256, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/projects/{project_id}/api-keys", EndpointConfig(access="authenticated", rate_by="user", rate_hits=10, rate_window=3600, max_body_bytes=256, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/projects/{project_id}/api-keys/{key_id}/revoke", EndpointConfig(access="authenticated", rate_by="user", rate_hits=10, rate_window=3600, max_body_bytes=64, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/projects/{project_id}/api-keys/{key_id}/rotate", EndpointConfig(access="authenticated", rate_by="user", rate_hits=5, rate_window=3600, max_body_bytes=64, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/billing/checkout", EndpointConfig(access="authenticated", rate_by="user", rate_hits=5, rate_window=3600, max_body_bytes=128, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/billing/cancel", EndpointConfig(access="authenticated", rate_by="user", rate_hits=3, rate_window=3600, max_body_bytes=0, idempotency=True)),
    ("POST", "/v1/core/organizations/{organization_id}/billing/upgrade", EndpointConfig(access="authenticated", rate_by="user", rate_hits=5, rate_window=3600, max_body_bytes=128, idempotency=True)),

    # --- Webhooks ---
    ("POST", "/v1/core/billing/stripe", EndpointConfig(access="public", rate_by="ip", rate_hits=100, rate_window=60, max_body_bytes=131072)),
]


STATIC_ENDPOINTS: dict[tuple[str, str], EndpointConfig] = {
    (method, path): config for method, path, config in ROUTE_MATRIX if "{" not in path
}


DYNAMIC_PATTERNS: list[tuple[str, re.Pattern[str], EndpointConfig, str]] = [
    (
        method,
        re.compile("^" + re.sub(r"\{[a-zA-Z0-9_]+\}", r"[^/]+", path) + "$", re.ASCII),
        config,
        path,
    )
    for method, path, config in ROUTE_MATRIX
    if "{" in path
]


@lru_cache(maxsize=4000)
def get_endpoint_config(method: str, path: str) -> EndpointConfig | None:
    normalized_method = method.upper()
    config = STATIC_ENDPOINTS.get((normalized_method, path))
    if config is not None:
        return config
    for entry_method, regex, dynamic_config, _ in DYNAMIC_PATTERNS:
        if entry_method == normalized_method and regex.match(path):
            return dynamic_config
    return None


@lru_cache(maxsize=4000)
def get_route_template(method: str, path: str) -> str:
    normalized_method = method.upper()
    if (normalized_method, path) in STATIC_ENDPOINTS:
        return path
    for entry_method, regex, _, template in DYNAMIC_PATTERNS:
        if entry_method == normalized_method and regex.match(path):
            return template
    return path
