from dataclasses import dataclass
from datetime import datetime, timezone

from asyncpg import Connection

from server.src.logic.core.billing.subscription.plan_price_maps import PRICE_PLAN_MAP
from server.src.store.sql.core.billing.subscriptions.update_subscription import update_subscription

@dataclass
class ParsedSubscription:
    price_id: str
    stripe_item_id: str
    plan: str
    status: str
    current_period_end: datetime
    cancel_at_period_end: bool
    trial_end: datetime | None

def parse_stripe_subscription(stripe_sub: dict) -> ParsedSubscription:
    price_id: str = stripe_sub["items"]["data"][0]["price"]["id"]
    trial_end_ts = stripe_sub.get("trial_end")
    return ParsedSubscription(
        price_id=price_id,
        stripe_item_id=stripe_sub["items"]["data"][0]["id"],
        plan=PRICE_PLAN_MAP.get(price_id, "unknown"),
        status=stripe_sub["status"],
        current_period_end=datetime.fromtimestamp(
            stripe_sub["current_period_end"], tz=timezone.utc
        ),
        cancel_at_period_end=stripe_sub["cancel_at_period_end"],
        trial_end=datetime.fromtimestamp(trial_end_ts, tz=timezone.utc) if trial_end_ts else None,
    )

async def sync_subscription(conn: Connection, stripe_sub: dict) -> None:
    parsed = parse_stripe_subscription(stripe_sub)
    await update_subscription(
        conn,
        stripe_subscription_id=stripe_sub["id"],
        status=parsed.status,
        plan=parsed.plan,
        current_period_end=parsed.current_period_end,
        cancel_at_period_end=parsed.cancel_at_period_end,
        trial_end=parsed.trial_end,
        stripe_item_id=parsed.stripe_item_id,
    )
