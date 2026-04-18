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

def _get_primary_subscription_item(stripe_sub: dict) -> dict:
    items = stripe_sub.get("items", {}).get("data", [])
    if not items:
        raise ValueError("Stripe subscription has no subscription items.")
    return items[0]


def _get_current_period_end_ts(stripe_sub: dict, item: dict) -> int:
    current_period_end_ts = item.get("current_period_end") or stripe_sub.get("current_period_end")
    if current_period_end_ts is None:
        raise ValueError("Stripe subscription is missing current_period_end.")
    return current_period_end_ts


def parse_stripe_subscription(stripe_sub: dict) -> ParsedSubscription:
    item = _get_primary_subscription_item(stripe_sub)
    price_id: str = item["price"]["id"]
    trial_end_ts = stripe_sub.get("trial_end")
    current_period_end_ts = _get_current_period_end_ts(stripe_sub, item)
    return ParsedSubscription(
        price_id=price_id,
        stripe_item_id=item["id"],
        plan=PRICE_PLAN_MAP.get(price_id, "unknown"),
        status=stripe_sub["status"],
        current_period_end=datetime.fromtimestamp(current_period_end_ts, tz=timezone.utc),
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
