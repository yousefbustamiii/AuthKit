from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.config.email_templates import OrgInvitationTemplate
from server.src.app.crypto.encryption.aes_encrypt import encrypt
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.crypto.tokens.invitation_token import generate_invitation_token
from server.src.app.errors.domains.authentication_errors import InvalidEmailError
from server.src.app.errors.domains.core_errors import OrgAccessDeniedError, OrgInvalidInviteRoleError, OrgInviteAlreadyMemberError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.validation.validate_email import validate_email
from server.src.store.sql.authentication.users.select_user_by_email_hash import select_user_by_email_hash
from server.src.store.sql.core.organizations.members.invitations.insert_invitation import insert_invitation
from server.src.store.sql.core.organizations.select_organization_name import select_organization_name
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

INVITATION_EXPIRE_DAYS = 7

@dataclass
class InvitationResult:
    invitation_id: UUID

async def invite_organization_member(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    initiator_user_id: UUID,
    organization_id: UUID,
    email: str,
    role: str,
) -> InvitationResult:
    ok, validated_email = validate_email(email)
    if not ok:
        raise InvalidEmailError(validated_email)

    if role not in ("admin", "member"):
        raise OrgInvalidInviteRoleError()

    initiator_membership = await resolve_user_role_in_org(pool, organization_id, initiator_user_id, org_role_cache)

    if initiator_membership.role not in ("owner", "admin"):
        raise OrgAccessDeniedError()

    # admin can only invite as member — inviting as admin is owner-only
    if initiator_membership.role == "admin" and role != "member":
        raise OrgInvalidInviteRoleError()

    email_hash = hash_blake2s(validated_email)
    email_encrypted = encrypt(validated_email)

    async with pool.acquire() as conn:
        org_name = await select_organization_name(conn, organization_id=organization_id)

        existing_user = await select_user_by_email_hash(conn, email_hash)
        if existing_user is not None:
            existing_membership = await resolve_user_role_in_org(pool, organization_id, existing_user.user_id, org_role_cache)
            if existing_membership.role is not None:
                raise OrgInviteAlreadyMemberError()

        invitation_token = generate_invitation_token()
        invitation_token_hash = hash_blake2s(invitation_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=INVITATION_EXPIRE_DAYS)

        invitation = await insert_invitation(
            conn,
            organization_id=organization_id,
            invited_by_user_id=initiator_user_id,
            email_hash=email_hash,
            email_encrypted=email_encrypted,
            invitation_token_hash=invitation_token_hash,
            role=role,
            expires_at=expires_at,
        )

    template = OrgInvitationTemplate(token=invitation_token, org_name=org_name, role=role)

    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": validated_email,
        "subject": template.subject,
        "message": template.html,
    })

    return InvitationResult(invitation_id=invitation.invitation_id)
