import asyncio

from fastapi import HTTPException
from starlette.requests import Request

from server.src.app.config.settings import settings
from server.src.app.middleware.phases.phase1.helpers.classify_ip_type import IPClassification, classify_ip_type
from server.src.app.middleware.phases.phase1.helpers.extract_country import extract_country
from server.src.app.middleware.phases.phase1.helpers.extract_device import extract_device

def extract_ip(request: Request) -> tuple[str, IPClassification]:
    if not request.client:
        raise HTTPException(status_code=400, detail="MISSING_CLIENT_INFO")

    if settings.cf_guard_enabled:
        ip = request.headers.get("CF-Connecting-IP", request.client.host).strip()
    else:
        proxy_count = settings.trusted_proxy_count
        if proxy_count == 0:
            ip = request.client.host.strip()
        else:
            xff = request.headers.get("X-Forwarded-For", "")
            ips = [x.strip() for x in xff.split(",") if x.strip()]
            if len(ips) >= proxy_count:
                ip = ips[-proxy_count]
            else:
                ip = request.client.host.strip()

    return ip, classify_ip_type(ip)


async def extract_identity(request: Request, ip: str, ip_classification: IPClassification) -> tuple[str, str]:
    raw_user_agent = request.headers.get("User-Agent", "")[:256]
    country, device = await asyncio.gather(
        extract_country(request, ip),
        extract_device(raw_user_agent),
    )
    return country, device
