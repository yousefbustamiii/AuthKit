from dataclasses import dataclass
from uuid import UUID

from asyncpg import Connection

@dataclass
class UserRoleInOrg:
    role: str | None
    owned_org_count: int

async def select_user_role_in_org(conn: Connection, organization_id: UUID, user_id: UUID) -> UserRoleInOrg:
    query = """
    SELECT
        (SELECT role FROM organization_members WHERE organization_id = $1 AND user_id = $2 AND is_deleted = FALSE) AS role,
        (SELECT COUNT(*) FROM organization_members WHERE user_id = $2 AND role = 'owner' AND is_deleted = FALSE) AS owned_org_count
    """
    row = await conn.fetchrow(query, organization_id, user_id)
    return UserRoleInOrg(role=row["role"], owned_org_count=row["owned_org_count"])
