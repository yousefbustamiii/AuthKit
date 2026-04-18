from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection


@dataclass
class OrganizationProjectRecord:
    project_id: UUID
    name: str
    created_by_user_id: UUID
    created_at: datetime

async def get_organization_projects(conn: Connection, organization_id: UUID) -> list[OrganizationProjectRecord]:
    query = """
    SELECT project_id, name, created_by_user_id, created_at
    FROM projects
    WHERE organization_id = $1
      AND is_deleted = FALSE
    ORDER BY created_at DESC
    """

    rows = await conn.fetch(query, organization_id)

    return [
        OrganizationProjectRecord(
            project_id=row["project_id"],
            name=row["name"],
            created_by_user_id=row["created_by_user_id"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
