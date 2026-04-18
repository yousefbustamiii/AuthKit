from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.encryption.aes_decrypt import decrypt

@dataclass
class UserProfile:
    user_id: UUID
    email: str
    password_hash: str | None
    name: str | None
    account_plan: str
    account_status: str
    provider: str
    avatar_url: str | None
    created_at: datetime

async def get_user_profile(conn: Connection, user_id: UUID) -> UserProfile | None:
    query = """
    SELECT
        user_id,
        email_encrypted,
        password_hash,
        name,
        account_plan,
        account_status,
        provider,
        avatar_url,
        created_at
    FROM users
    WHERE user_id = $1
      AND is_deleted = FALSE
    """

    row = await conn.fetchrow(query, user_id)

    if row is None:
        return None

    return UserProfile(
        user_id=row["user_id"],
        email=decrypt(row["email_encrypted"]),
        password_hash=row["password_hash"],
        name=row["name"],
        account_plan=row["account_plan"],
        account_status=row["account_status"],
        provider=row["provider"],
        avatar_url=row["avatar_url"],
        created_at=row["created_at"],
    )
