from dataclasses import dataclass
from uuid import UUID

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.errors.domains.core_errors import InvalidOrgNameError
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.app.validation.core.validate_core_names import validate_org_name
from server.src.store.sql.core.organizations.insert_organization import insert_organization
from server.src.store.sql.core.organizations.members.insert_organization_member import insert_organization_member

@dataclass
class CreatedOrganization:
    organization_id: UUID
    organization_member_id: UUID

async def create_organization(
    pool: Pool,
    cache: Redis,
    user_id: UUID,
    name: str,
) -> CreatedOrganization:
    ok, result = validate_org_name(name)
    if not ok:
        raise InvalidOrgNameError(result)

    validated_name = result

    async with pool.acquire() as conn:
        async with conn.transaction():
            org = await insert_organization(conn, name=validated_name, owner_user_id=user_id)
            member = await insert_organization_member(conn, organization_id=org.organization_id, user_id=user_id)

    await RedisEventPublisher(cache).publish(
        "org_role:invalidation",
        "INVALIDATE_USER_ORG_ROLES",
        {"user_id": str(user_id)},
    )

    return CreatedOrganization(
        organization_id=org.organization_id,
        organization_member_id=member.organization_member_id,
    )
