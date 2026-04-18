from dataclasses import dataclass
from uuid import UUID

from asyncpg import Connection

@dataclass
class ApiKeyByHash:
    key_id: UUID
    project_id: UUID
    organization_id: UUID
    plan: str
    status: str | None

async def select_api_key_by_hash(
    conn: Connection,
    key_hash: str,
) -> ApiKeyByHash | None:
    query = """
    SELECT
        ak.key_id,
        ak.project_id,
        p.organization_id,
        COALESCE(s.plan, 'free') AS plan,
        s.status
    FROM api_keys ak
    JOIN projects p
        ON p.project_id = ak.project_id
       AND p.is_deleted = FALSE
    LEFT JOIN subscriptions s
        ON s.organization_id = p.organization_id
       AND s.is_deleted = FALSE
       AND s.status != 'canceled'
    WHERE ak.key_hash = $1
      AND ak.is_deleted = FALSE
    """

    row = await conn.fetchrow(query, key_hash)

    if row is None:
        return None

    return ApiKeyByHash(
        key_id=row["key_id"],
        project_id=row["project_id"],
        organization_id=row["organization_id"],
        plan=row["plan"],
        status=row["status"],
    )
