import httpx

from server.src.app.config.settings import settings
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

async def send_email(http: httpx.AsyncClient, email: str, subject: str, message: str) -> None:
    body = {
        "personalizations": [{"to": [{"email": email}]}],
        "from": {"email": settings.sendgrid.sender_email},
        "subject": subject,
        "content": [{"type": "text/html", "value": message}]
    }
    headers = {"Authorization": f"Bearer {settings.sendgrid.api_key}"}
    try:
        response = await http.post(settings.sendgrid.api_url, json=body, headers=headers)
        response.raise_for_status()
    except Exception:
        logger.exception("email_send_failed", extra={"email_hash": hash_blake2s(email)})