from functools import lru_cache

from fastapi import HTTPException
from user_agents import parse

class BotDetected(Exception):
    pass

@lru_cache(maxsize=2000)
def parse_and_extract(user_agent_string: str) -> str:
    if not user_agent_string:
        return "Unknown"

    ua = parse(user_agent_string)

    if ua.is_bot:
        raise BotDetected()

    # Device
    if ua.device.family and ua.device.family != "Other":
        device = ua.device.family
    elif ua.is_tablet:
        device = "Tablet"
    elif ua.is_mobile:
        device = "Mobile"
    elif ua.is_pc:
        device = "PC"
    else:
        device = "Unknown"

    # Brand and model for mobile/tablet
    brand = ua.device.brand or ""
    model = ua.device.model or ""
    device_full = f"{brand} {model}".strip() if brand or model else device

    # OS with version
    os_name = ua.os.family or "Unknown OS"
    os_version = ".".join(str(v) for v in ua.os.version if v)
    os_full = f"{os_name} {os_version}".strip() if os_version else os_name

    return f"{device_full} ({os_full})"


async def extract_device(user_agent_string: str) -> str:
    try:
        return parse_and_extract(user_agent_string)
    except BotDetected:
        raise HTTPException(status_code=403, detail="BOT_NOT_ALLOWED")
