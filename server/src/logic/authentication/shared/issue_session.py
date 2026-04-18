from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.tokens.session_tokens import generate_session_token
from server.src.store.sql.authentication.sessions.insert_session import insert_session

@dataclass
class IssuedSession:
    session_token: str
    session_id: UUID
    expires_at: datetime
    device_id: UUID | None
    killed_session_token_hash: str | None

async def issue_session(
    conn: Connection,
    user_id: UUID,
    country: str,
    device: str,
    device_id: UUID | None = None,
) -> IssuedSession:
    token = generate_session_token()
    result = await insert_session(conn, user_id, token, country, device, device_id=device_id)
    return IssuedSession(
        session_token=token,
        session_id=result.session_id,
        expires_at=result.expires_at,
        device_id=device_id,
        killed_session_token_hash=result.killed_session_token_hash,
    )
