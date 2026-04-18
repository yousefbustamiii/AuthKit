from functools import lru_cache

from starlette.responses import Response

from server.src.app.config.settings import settings

ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "X-Idempotency-Key",
    "X-Client-Type",
    "X-Device-Token",
    "X-Requested-With",
    "Accept",
    "Origin",
    "User-Agent",
]

ALLOWED_METHODS = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATCH",
]

@lru_cache(maxsize=256)
def build_cors_headers(origin: str | None) -> tuple[tuple[bytes, bytes], ...]:
    headers = []
    if origin and origin in settings.cors_allowed_origins:
        headers.append((b"access-control-allow-origin", origin.encode("latin-1")))
        headers.append((b"access-control-allow-credentials", b"true"))
        headers.append((b"vary", b"Origin"))
        headers.append((b"access-control-allow-methods", ", ".join(ALLOWED_METHODS).encode("latin-1")))
        headers.append((b"access-control-allow-headers", ", ".join(ALLOWED_HEADERS).encode("latin-1")))
        headers.append((b"access-control-max-age", b"600"))

    headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains; preload"))
    headers.append((b"x-content-type-options", b"nosniff"))
    headers.append((b"referrer-policy", b"strict-origin-when-cross-origin"))
    headers.append((b"permissions-policy", b"geolocation=(), microphone=(), camera=(), payment=(), usb=()"))
    return tuple(headers)

get_cors_headers = build_cors_headers

def handle_cors_preflight(origin: str | None) -> Response:
    headers = [(k.decode("latin-1"), v.decode("latin-1")) for k, v in build_cors_headers(origin)]
    return Response(status_code=204, headers=dict(headers))
