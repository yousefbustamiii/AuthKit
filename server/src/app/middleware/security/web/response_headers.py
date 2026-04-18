from server.src.app.middleware.security.web.cors_handler import get_cors_headers
from server.src.app.middleware.security.web.csp_handler import get_csp_headers

def build_response_headers(origin: str | None, ctx, request) -> list[tuple[bytes, bytes]]:
    headers = list(get_cors_headers(origin))
    if ctx and ctx.endpoint_config and ctx.endpoint_config.csp and request.method == "GET":
        headers.extend(get_csp_headers(request))
    return headers
