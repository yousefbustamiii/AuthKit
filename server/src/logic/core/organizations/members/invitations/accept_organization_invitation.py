from uuid import UUID

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.errors.domains.authentication_errors import UserNotFoundError
from server.src.app.errors.domains.core_errors import OrgInvitationInvalidKeyError, OrgInvitationNotFoundError
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.app.validation.core.validate_invitation_key import validate_invitation_key
from server.src.store.sql.authentication.users.select_user_by_id import select_user_by_id
from server.src.store.sql.core.organizations.members.insert_organization_member import insert_organization_member
from server.src.store.sql.core.organizations.members.invitations.select_invitation_by_hash import select_invitation_by_hash
from server.src.store.sql.core.organizations.members.invitations.soft_delete_invitation import soft_delete_invitation

async def accept_organization_invitation(
    pool: Pool,
    cache: Redis,
    user_id: UUID,
    invitation_key: str,
) -> None:
    ok, validated_key = validate_invitation_key(invitation_key)
    if not ok:
        raise OrgInvitationInvalidKeyError()

    async with pool.acquire() as conn:
        user = await select_user_by_id(conn, user_id)
        if user is None:
            raise UserNotFoundError()

        invitation_token_hash = hash_blake2s(validated_key)

        invitation = await select_invitation_by_hash(
            conn,
            invitation_token_hash=invitation_token_hash,
            email_hash=user.email_hash,
        )
        if invitation is None:
            raise OrgInvitationNotFoundError()

        async with conn.transaction():
            await insert_organization_member(
                conn,
                organization_id=invitation.organization_id,
                user_id=user_id,
                role=invitation.role,
                invited_by_user_id=invitation.invited_by_user_id,
            )
            await soft_delete_invitation(conn, invitation_id=invitation.invitation_id)

    await RedisEventPublisher(cache).publish(
        "org_role:invalidation",
        "INVALIDATE_ORG_ROLE_CACHE",
        {"organization_id": str(invitation.organization_id), "user_id": str(user_id)},
    )
