from dataclasses import dataclass
from typing import Literal
from uuid import UUID, uuid7

from asyncpg import Connection

from server.src.app.crypto.encryption.aes_encrypt import encrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s

Provider = Literal["email", "google", "github"]

@dataclass
class InsertedUser:
    user_id: UUID

async def insert_user(
    conn: Connection,
    email: str,
    provider: Provider,
    password_hash: str | None = None,
    name: str | None = None,
    avatar_url: str | None = None,
) -> InsertedUser:
    email_encrypted = encrypt(email)
    email_hash = hash_blake2s(email)
    user_id = uuid7()

    query = """
    INSERT INTO users (user_id, email_encrypted, email_hash, password_hash, provider, name, avatar_url)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING user_id
    """

    row = await conn.fetchrow(
        query,
        user_id,
        email_encrypted,
        email_hash,
        password_hash,
        provider,
        name,
        avatar_url,
    )

    return InsertedUser(user_id=row["user_id"])
