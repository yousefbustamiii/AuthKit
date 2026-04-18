from datetime import datetime, timezone

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import BillingSubscriptionStartedTemplate
from server.src.app.config.stripe_client import retrieve_stripe_subscription
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.events.event_emitter import event_emitter
from server.src.logic.core.billing.subscription.sync_subscription import parse_stripe_subscription
from server.src.store.sql.core.billing.customers.select_customer_by_stripe_id import select_customer_by_stripe_id
from server.src.store.sql.core.billing.subscriptions.insert_subscription import insert_subscription
from server.src.store.sql.core.organizations.select_org_owner import select_org_owner

async def handle_checkout_session_completed(pool: Pool, cache: Redis, data_obj: dict) -> None:
    stripe_sub_id: str | None = data_obj.get("subscription")
    stripe_customer_id: str | None = data_obj.get("customer")

    if not stripe_sub_id or not stripe_customer_id:
        return

    async with pool.acquire() as conn:
        customer = await select_customer_by_stripe_id(conn, stripe_customer_id)

    if customer is None:
        return

    stripe_sub = await retrieve_stripe_subscription(stripe_sub_id)
    parsed = parse_stripe_subscription(stripe_sub)

    async with pool.acquire() as conn:
        await insert_subscription(
            conn,
            organization_id=customer.organization_id,
            customer_id=customer.customer_id,
            stripe_subscription_id=stripe_sub_id,
            stripe_item_id=parsed.stripe_item_id,
            plan=parsed.plan,
            status=parsed.status,
            current_period_end=parsed.current_period_end,
            cancel_at_period_end=parsed.cancel_at_period_end,
            trial_end=parsed.trial_end,
        )
        owner = await select_org_owner(conn, customer.organization_id)

    if owner is None:
        return

    email = decrypt(owner.email_encrypted)
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    next_billing_date = parsed.current_period_end.strftime("%B %d, %Y")
    template = BillingSubscriptionStartedTemplate(
        org_name=owner.org_name,
        plan=parsed.plan.replace("_", " ").title(),
        next_billing_date=next_billing_date,
        timestamp=timestamp,
    )
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email,
        "subject": template.subject,
        "message": template.html,
    })
