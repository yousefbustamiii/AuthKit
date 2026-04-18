from dataclasses import dataclass
from uuid import UUID, uuid7

from asyncpg import Connection

@dataclass
class InsertedOrganization:
    organization_id: UUID

async def insert_organization(
    conn: Connection,
    name: str,
    owner_user_id: UUID,
) -> InsertedOrganization:
    organization_id = uuid7()

    query = """
    INSERT INTO organizations (organization_id, name, owner_user_id)
    VALUES ($1, $2, $3)
    RETURNING organization_id
    """

    row = await conn.fetchrow(query, organization_id, name, owner_user_id)

    return InsertedOrganization(organization_id=row["organization_id"])
