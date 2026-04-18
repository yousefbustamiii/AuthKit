from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.config.email_templates import BillingCancelTemplate
from server.src.app.config.stripe_client import cancel_stripe_subscription
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.errors.domains.authentication_errors import UserNotFoundError
from server.src.app.errors.domains.billing_errors import ActiveSubscriptionNotFoundError, SubscriptionAlreadyScheduledForCancellationError
from server.src.app.errors.domains.core_errors import OrgAccessDeniedError, OrgNotFoundError
from server.src.app.events.event_emitter import event_emitter
from server.src.store.sql.authentication.users.select_user_by_id import select_user_by_id
from server.src.store.sql.core.billing.subscriptions.select_subscription_by_org import select_subscription_by_org
from server.src.store.sql.core.organizations.select_organization_name import select_organization_name
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

async def cancel_subscription(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
) -> None:
    membership = await resolve_user_role_in_org(pool, organization_id, user_id, org_role_cache)
    if membership.role != "owner":
        raise OrgAccessDeniedError()

    async with pool.acquire() as conn:
        sub = await select_subscription_by_org(conn, organization_id)
        if sub is None:
            raise ActiveSubscriptionNotFoundError()

        if sub.status == "canceled":
            raise ActiveSubscriptionNotFoundError()

        if sub.cancel_at_period_end:
            raise SubscriptionAlreadyScheduledForCancellationError()

        org_name = await select_organization_name(conn, organization_id)
        if org_name is None:
            raise OrgNotFoundError()

        user = await select_user_by_id(conn, user_id)
        if user is None:
            raise UserNotFoundError()

    email = decrypt(user.email_encrypted)

    await cancel_stripe_subscription(sub.stripe_subscription_id, at_period_end=True)

    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = BillingCancelTemplate(
        org_name=org_name,
        plan=sub.plan.replace("_", " ").title(),
        period_end=sub.current_period_end.strftime("%B %d, %Y"),
        timestamp=timestamp,
    )
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email,
        "subject": template.subject,
        "message": template.html,
    })

