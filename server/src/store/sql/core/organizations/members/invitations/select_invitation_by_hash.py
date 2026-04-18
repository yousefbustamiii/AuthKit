from dataclasses import dataclass
from uuid import UUID

from asyncpg import Connection

@dataclass
class InvitationByHash:
    invitation_id: UUID
    organization_id: UUID
    invited_by_user_id: UUID
    role: str


async def select_invitation_by_hash(
    conn: Connection,
    invitation_token_hash: str,
    email_hash: str,
) -> InvitationByHash | None:
    query = """
    SELECT invitation_id, organization_id, invited_by_user_id, role
    FROM invitations
    WHERE invitation_token_hash = $1
      AND email_hash = $2
      AND is_deleted = FALSE
      AND expires_at > NOW()
    """
    row = await conn.fetchrow(query, invitation_token_hash, email_hash)
    if row is None:
        return None
    return InvitationByHash(
        invitation_id=row["invitation_id"],
        organization_id=row["organization_id"],
        invited_by_user_id=row["invited_by_user_id"],
        role=row["role"],
    )
