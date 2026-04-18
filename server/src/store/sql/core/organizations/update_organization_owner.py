from uuid import UUID

from asyncpg import Connection

async def update_organization_owner(
    conn: Connection,
    organization_id: UUID,
    owner_user_id: UUID,
) -> None:
    query = """
    UPDATE organizations
    SET owner_user_id = $2
    WHERE organization_id = $1 AND is_deleted = FALSE
    """
    await conn.execute(query, organization_id, owner_user_id)
