from dataclasses import dataclass
from uuid import UUID, uuid7

from asyncpg import Connection

@dataclass
class InsertedProject:
    project_id: UUID

async def insert_project(
    conn: Connection,
    organization_id: UUID,
    name: str,
    created_by_user_id: UUID,
) -> InsertedProject:
    project_id = uuid7()

    query = """
    INSERT INTO projects (project_id, organization_id, name, created_by_user_id)
    VALUES ($1, $2, $3, $4)
    RETURNING project_id
    """

    row = await conn.fetchrow(query, project_id, organization_id, name, created_by_user_id)

    return InsertedProject(project_id=row["project_id"])
