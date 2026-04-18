from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.errors.domains.core_errors import OrgAccessDeniedError, OrgInvitationNotFoundError
from server.src.store.sql.core.organizations.members.invitations.soft_delete_invitation import soft_delete_invitation
from server.src.store.sql.core.organizations.members.invitations.soft_delete_invitation_exact import soft_delete_invitation_exact
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

async def cancel_organization_invitation(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
    invitation_id: UUID,
) -> None:
    membership = await resolve_user_role_in_org(pool, organization_id, user_id, org_role_cache)

    if membership.role not in ("owner", "admin"):
        raise OrgAccessDeniedError()

    async with pool.acquire() as conn:
        if membership.role == "owner":
            deleted = await soft_delete_invitation(conn, invitation_id=invitation_id)
        else:
            deleted = await soft_delete_invitation_exact(
                conn,
                invitation_id=invitation_id,
                invited_by_user_id=user_id,
            )

        if not deleted:
            raise OrgInvitationNotFoundError()
