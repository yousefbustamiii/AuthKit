from dataclasses import dataclass
from uuid import UUID

from server.src.app.middleware.phases.phase1.endpoint_matrix import EndpointConfig
from server.src.app.middleware.phases.phase1.helpers.classify_ip_type import IPClassification

@dataclass
class RequestContext:
    ip: str
    method: str
    path: str
    route_template: str
    endpoint_config: EndpointConfig | None
    session_token: str | None
    api_key_token: str | None
    idempotency_key: str | None
    country: str
    device: str
    ip_classification: IPClassification | None = None
    user_id: UUID | None = None
    key_id: UUID | None = None
    org_id: UUID | None = None
    project_id: UUID | None = None
    plan: str | None = None
    idempotency_lock_acquired: bool = False
    client_type: str = "web"
