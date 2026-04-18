from uuid import UUID

from asyncpg import Connection

async def update_organization_member_role(
    conn: Connection,
    organization_id: UUID,
    user_id: UUID,
    role: str,
) -> None:
    query = """
    UPDATE organization_members
    SET role = $3
    WHERE organization_id = $1 AND user_id = $2 AND is_deleted = FALSE
    """
    await conn.execute(query, organization_id, user_id, role)
