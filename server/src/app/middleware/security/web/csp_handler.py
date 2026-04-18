import secrets

from starlette.requests import Request

def generate_csp_nonce() -> str:
    return secrets.token_urlsafe(32)

def get_csp_headers(request: Request) -> list[tuple[bytes, bytes]]:
    nonce = request.state.csp_nonce
    policy = (
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}' 'strict-dynamic'; "
        f"style-src 'self' 'nonce-{nonce}'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "connect-src 'self' wss:; "
        "worker-src 'self' blob:; "
        "manifest-src 'self'; "
        "upgrade-insecure-requests; "
        "block-all-mixed-content;"
    )
    return [(b"content-security-policy", policy.encode("latin-1"))]