from dataclasses import dataclass
from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.store.sql.authentication.users.select_user_by_email_hash import select_user_by_email_hash

@dataclass
class OAuthIdentity:
    user_id: UUID
    email: str

async def lookup_oauth_identity(
    conn: Connection,
    email: str,
) -> OAuthIdentity | None:
    email_hash = hash_blake2s(email)

    row = await select_user_by_email_hash(conn, email_hash)
    if row is None:
        return None

    plaintext_email = decrypt(row.email_encrypted)
    return OAuthIdentity(user_id=row.user_id, email=plaintext_email)
