from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

@dataclass
class SessionByTokenHash:
    session_id: UUID
    user_id: UUID
    expires_at: datetime
    device_id: UUID | None
    account_status: str

async def select_session_by_token_hash(conn: Connection, session_token: str) -> SessionByTokenHash | None:
    session_token_hash = hash_blake2s(session_token)
    
    query = """
    SELECT 
        s.session_id, 
        s.user_id, 
        s.expires_at,
        s.device_id,
        u.account_status
    FROM sessions s
    JOIN users u ON s.user_id = u.user_id
    WHERE s.session_token_hash = $1
      AND u.is_deleted = FALSE
      AND s.expires_at > NOW()
    """
    
    row = await conn.fetchrow(query, session_token_hash)
    
    if row is None:
        return None
        
    return SessionByTokenHash(
        session_id=row["session_id"],
        user_id=row["user_id"],
        expires_at=row["expires_at"],
        device_id=row["device_id"],
        account_status=row["account_status"]
    )
