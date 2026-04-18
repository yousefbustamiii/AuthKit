from dataclasses import dataclass
from uuid import UUID

from asyncpg import Connection

@dataclass
class UserByUserId:
    user_id: UUID
    email_encrypted: str
    email_hash: str
    password_hash: str | None
    provider: str

async def select_user_by_id(conn: Connection, user_id: UUID) -> UserByUserId | None:
    query = """
    SELECT user_id, email_encrypted, email_hash, password_hash, provider
    FROM users
    WHERE user_id = $1 AND is_deleted = FALSE
    """

    row = await conn.fetchrow(query, user_id)

    if row is None:
        return None

    return UserByUserId(
        user_id=row["user_id"],
        email_encrypted=row["email_encrypted"],
        email_hash=row["email_hash"],
        password_hash=row["password_hash"],
        provider=row["provider"],
    )
