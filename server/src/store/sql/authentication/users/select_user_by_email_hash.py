from dataclasses import dataclass
from uuid import UUID

from asyncpg import Connection

@dataclass
class UserByEmailHash:
    user_id: UUID
    is_deleted: bool
    password_hash: str | None
    email_encrypted: str

async def select_user_by_email_hash(conn: Connection, email_hash: str) -> UserByEmailHash | None:
    query = """
    SELECT user_id, is_deleted, password_hash, email_encrypted
    FROM users
    WHERE email_hash = $1 AND is_deleted = FALSE
    """

    row = await conn.fetchrow(query, email_hash)

    if row is None:
        return None

    return UserByEmailHash(
        user_id=row["user_id"],
        is_deleted=row["is_deleted"],
        password_hash=row["password_hash"],
        email_encrypted=row["email_encrypted"],
    )
