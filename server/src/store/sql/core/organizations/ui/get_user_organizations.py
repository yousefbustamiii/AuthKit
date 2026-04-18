from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection


@dataclass
class UserOrganization:
    organization_id: UUID
    name: str
    owner_user_id: UUID
    current_user_role: str
    created_at: datetime


async def get_user_organizations(conn: Connection, user_id: UUID) -> list[UserOrganization]:
    query = """
    SELECT
        o.organization_id,
        o.name,
        o.owner_user_id,
        om.role AS current_user_role,
        o.created_at
    FROM organizations o
    JOIN organization_members om
      ON om.organization_id = o.organization_id
     AND om.user_id = $1
     AND om.is_deleted = FALSE
    WHERE o.is_deleted = FALSE
    ORDER BY o.created_at DESC
    """

    rows = await conn.fetch(query, user_id)

    return [
        UserOrganization(
            organization_id=row["organization_id"],
            name=row["name"],
            owner_user_id=row["owner_user_id"],
            current_user_role=row["current_user_role"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
