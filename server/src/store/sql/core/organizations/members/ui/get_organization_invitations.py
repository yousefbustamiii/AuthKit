from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.encryption.aes_decrypt import decrypt


@dataclass
class OrganizationInvitationRecord:
    invitation_id: UUID
    email: str
    role: str
    invited_by_user_id: UUID
    created_at: datetime
    expires_at: datetime


async def get_organization_invitations(conn: Connection, organization_id: UUID) -> list[OrganizationInvitationRecord]:
    query = """
    SELECT
        invitation_id,
        email_encrypted,
        role,
        invited_by_user_id,
        created_at,
        expires_at
    FROM invitations
    WHERE organization_id = $1
      AND is_deleted = FALSE
      AND expires_at > NOW()
    ORDER BY created_at DESC
    """

    rows = await conn.fetch(query, organization_id)

    return [
        OrganizationInvitationRecord(
            invitation_id=row["invitation_id"],
            email=decrypt(row["email_encrypted"]),
            role=row["role"],
            invited_by_user_id=row["invited_by_user_id"],
            created_at=row["created_at"],
            expires_at=row["expires_at"],
        )
        for row in rows
    ]
