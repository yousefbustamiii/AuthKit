from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

from server.src.app.crypto.encryption.aes_decrypt import decrypt


@dataclass
class OrganizationMemberRecord:
    organization_member_id: UUID
    user_id: UUID
    email: str
    name: str | None
    avatar_url: str | None
    role: str
    invited_by_user_id: UUID | None
    created_at: datetime


async def get_organization_members(conn: Connection, organization_id: UUID) -> list[OrganizationMemberRecord]:
    query = """
    SELECT
        om.organization_member_id,
        om.user_id,
        u.email_encrypted,
        u.name,
        u.avatar_url,
        om.role,
        om.invited_by_user_id,
        om.created_at
    FROM organization_members om
    JOIN users u ON u.user_id = om.user_id
    WHERE om.organization_id = $1
      AND om.is_deleted = FALSE
      AND u.is_deleted = FALSE
    ORDER BY
      CASE om.role
        WHEN 'owner' THEN 0
        WHEN 'admin' THEN 1
        ELSE 2
      END,
      om.created_at ASC
    """

    rows = await conn.fetch(query, organization_id)

    return [
        OrganizationMemberRecord(
            organization_member_id=row["organization_member_id"],
            user_id=row["user_id"],
            email=decrypt(row["email_encrypted"]),
            name=row["name"],
            avatar_url=row["avatar_url"],
            role=row["role"],
            invited_by_user_id=row["invited_by_user_id"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
