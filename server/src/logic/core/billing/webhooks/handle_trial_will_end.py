from datetime import datetime, timezone

from asyncpg import Pool
from redis.asyncio import Redis

from server.src.app.config.email_templates import BillingTrialEndingTemplate
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.events.event_emitter import event_emitter
from server.src.store.sql.core.billing.subscriptions.select_subscription_by_stripe_id import select_subscription_by_stripe_id
from server.src.store.sql.core.organizations.select_org_owner import select_org_owner

async def handle_trial_will_end(pool: Pool, cache: Redis, data_obj: dict) -> None:
    stripe_sub_id: str | None = data_obj.get("id")
    if not stripe_sub_id:
        return

    trial_end_ts = data_obj.get("trial_end")
    if not trial_end_ts:
        return

    async with pool.acquire() as conn:
        sub = await select_subscription_by_stripe_id(conn, stripe_sub_id)
        if sub is None:
            return
        owner = await select_org_owner(conn, sub.organization_id)

    if owner is None:
        return

    email = decrypt(owner.email_encrypted)
    trial_end_date = datetime.fromtimestamp(trial_end_ts, tz=timezone.utc).strftime("%B %d, %Y")
    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = BillingTrialEndingTemplate(
        org_name=owner.org_name,
        plan=sub.plan.replace("_", " ").title(),
        trial_end_date=trial_end_date,
        timestamp=timestamp,
    )
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": email,
        "subject": template.subject,
        "message": template.html,
    })
