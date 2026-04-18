from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid7

from asyncpg import Connection

from server.src.app.config.settings import settings
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

@dataclass
class InsertedSession:
    session_id: UUID
    expires_at: datetime
    killed_session_token_hash: str | None

async def insert_session(
    conn: Connection,
    user_id: UUID,
    session_token: str,
    country: str,
    device: str,
    device_id: UUID | None = None,
) -> InsertedSession:
    session_token_hash = hash_blake2s(session_token)
    session_id = uuid7()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.session.expire_days)

    query = """
    WITH to_kill AS (
        SELECT session_id
        FROM sessions
        WHERE user_id = $2
          AND expires_at > NOW()
        ORDER BY created_at DESC
        OFFSET 4
    ),
    killed_info AS (
        UPDATE sessions
        SET expires_at = NOW()
        WHERE session_id IN (SELECT session_id FROM to_kill)
        RETURNING session_token_hash
    ),
    inserted AS (
        INSERT INTO sessions (session_id, user_id, device_id, session_token_hash, country, device, expires_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING session_id, expires_at
    )
    SELECT 
        i.session_id, 
        i.expires_at,
        (SELECT session_token_hash FROM killed_info LIMIT 1) AS killed_session_token_hash
    FROM inserted i
    """

    row = await conn.fetchrow(query, session_id, user_id, device_id, session_token_hash, country, device, expires_at)

    return InsertedSession(
        session_id=row["session_id"],
        expires_at=row["expires_at"],
        killed_session_token_hash=row["killed_session_token_hash"]
    )
