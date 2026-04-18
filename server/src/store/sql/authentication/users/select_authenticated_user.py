from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

@dataclass
class AuthenticatedUser:
    session_id: UUID
    user_id: UUID
    email: str
    account_status: str
    expires_at: datetime
    created_at: datetime

async def select_authenticated_user(
    conn: Connection,
    session_token: str
) -> AuthenticatedUser | None:

    session_token_hash = hash_blake2s(session_token)

    query = """
    SELECT 
        s.session_id,
        s.user_id,
        s.expires_at,
        u.email_encrypted,
        u.account_status,
        u.created_at
    FROM sessions s
    JOIN users u ON s.user_id = u.user_id
    WHERE 
        s.session_token_hash = $1
        AND s.expires_at > NOW()
        AND u.is_deleted = FALSE
    """

    row = await conn.fetchrow(query, session_token_hash)

    if row is None:
        return None

    return AuthenticatedUser(
        session_id=row["session_id"],
        user_id=row["user_id"],
        email=decrypt(row["email_encrypted"]),
        account_status=row["account_status"],
        expires_at=row["expires_at"],
        created_at=row["created_at"],
    )