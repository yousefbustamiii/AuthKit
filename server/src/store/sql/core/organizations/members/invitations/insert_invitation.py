from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid7

from asyncpg import Connection

@dataclass
class InsertedInvitation:
    invitation_id: UUID


async def insert_invitation(
    conn: Connection,
    organization_id: UUID,
    invited_by_user_id: UUID,
    email_hash: str,
    email_encrypted: str,
    invitation_token_hash: str,
    role: str,
    expires_at: datetime,
) -> InsertedInvitation:
    invitation_id = uuid7()

    query = """
    WITH invalidated AS (
        UPDATE invitations
        SET is_deleted = TRUE, expires_at = NOW()
        WHERE organization_id = $2 AND email_hash = $4 AND is_deleted = FALSE
    )
    INSERT INTO invitations (
        invitation_id, organization_id, invited_by_user_id, email_hash,
        email_encrypted, invitation_token_hash, role, expires_at
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    RETURNING invitation_id
    """

    row = await conn.fetchrow(
        query,
        invitation_id,
        organization_id,
        invited_by_user_id,
        email_hash,
        email_encrypted,
        invitation_token_hash,
        role,
        expires_at,
    )

    return InsertedInvitation(invitation_id=row["invitation_id"])
