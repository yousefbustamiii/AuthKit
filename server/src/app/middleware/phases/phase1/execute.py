from starlette.requests import Request

from server.src.app.middleware.phases.phase1.endpoint_matrix import get_endpoint_config, get_route_template
from server.src.app.middleware.phases.phase1.extract_identity import extract_identity
from server.src.app.middleware.phases.phase1.helpers.classify_ip_type import IPClassification
from server.src.app.middleware.phases.phase1.helpers.extract_country import extract_country
from server.src.app.middleware.phases.phase1.request_context import RequestContext

async def execute_phase_1(request: Request, ip: str, ip_classification: IPClassification | None) -> RequestContext:
    method = request.method
    path = request.url.path
    endpoint_config = get_endpoint_config(method, path)
    route_template = get_route_template(method, path)

    session_token = request.cookies.get("X-Session-Token") or None
    if not session_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_token = auth_header[7:].strip() or None

    api_key_token = request.headers.get("X-API-Key") or None

    is_api_key_request = (
        api_key_token is not None
        and endpoint_config is not None
        and (
            endpoint_config.access == "api_key"
            or (endpoint_config.access == "hybrid" and not session_token)
        )
    )

    if is_api_key_request:
        country = await extract_country(request, ip)
        device = "Server"
    else:
        country, device = await extract_identity(request, ip, ip_classification)
    idempotency_key = request.headers.get("X-Idempotency-Key")

    client_type_raw = request.headers.get("X-Client-Type", "web").lower().strip()
    client_type = client_type_raw if client_type_raw in ("web", "mobile") else "web"

    return RequestContext(
        ip=ip,
        method=method,
        path=path,
        route_template=route_template,
        endpoint_config=endpoint_config,
        session_token=session_token,
        api_key_token=api_key_token,
        idempotency_key=idempotency_key,
        country=country,
        device=device,
        ip_classification=ip_classification,
        client_type=client_type,
    )
