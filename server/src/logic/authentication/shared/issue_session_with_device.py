from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.tokens.device_tokens import generate_device_token
from server.src.app.crypto.tokens.session_tokens import generate_session_token
from server.src.store.sql.authentication.devices.insert_device import insert_device
from server.src.store.sql.authentication.sessions.insert_session import insert_session

@dataclass
class IssuedSessionWithDevice:
    session_token: str
    device_token: str
    session_id: UUID
    expires_at: datetime
    device_id: UUID
    killed_session_token_hash: str | None

async def issue_session_with_device(
    conn: Connection,
    user_id: UUID,
    country: str,
    device: str,
) -> IssuedSessionWithDevice:
    session_token = generate_session_token()
    device_token = generate_device_token()

    device_result = await insert_device(conn, user_id, device_token, device)
    session_result = await insert_session(
        conn, user_id, session_token, country, device,
        device_id=device_result.device_id
    )

    return IssuedSessionWithDevice(
        session_token=session_token,
        device_token=device_token,
        session_id=session_result.session_id,
        expires_at=session_result.expires_at,
        device_id=device_result.device_id,
        killed_session_token_hash=session_result.killed_session_token_hash,
    )
