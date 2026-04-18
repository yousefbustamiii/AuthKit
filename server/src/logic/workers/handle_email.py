import httpx
from pydantic import BaseModel

from server.src.logic.authentication.shared.send_email import send_email

class EmailEventPayload(BaseModel):
    email: str
    subject: str
    message: str

async def handle_email_event(http: httpx.AsyncClient, payload_dict: dict) -> None:
    payload = EmailEventPayload(**payload_dict)
    await send_email(http, payload.email, payload.subject, payload.message)
