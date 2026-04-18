from dataclasses import dataclass
from uuid import UUID, uuid7

from asyncpg import Connection

@dataclass
class InsertedOrganizationMember:
    organization_member_id: UUID

async def insert_organization_member(
    conn: Connection,
    organization_id: UUID,
    user_id: UUID,
    role: str | None = None,
    invited_by_user_id: UUID | None = None,
) -> InsertedOrganizationMember:
    organization_member_id = uuid7()

    if role is None:
        query = """
        INSERT INTO organization_members (organization_member_id, organization_id, user_id, invited_by_user_id)
        VALUES ($1, $2, $3, $4)
        RETURNING organization_member_id
        """
        row = await conn.fetchrow(query, organization_member_id, organization_id, user_id, invited_by_user_id)
    else:
        query = """
        INSERT INTO organization_members (organization_member_id, organization_id, user_id, role, invited_by_user_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING organization_member_id
        """
        row = await conn.fetchrow(query, organization_member_id, organization_id, user_id, role, invited_by_user_id)

    return InsertedOrganizationMember(organization_member_id=row["organization_member_id"])
