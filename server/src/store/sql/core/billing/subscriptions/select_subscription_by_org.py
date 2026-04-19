from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from asyncpg import Connection

@dataclass
class SubscriptionByOrg:
    subscription_id: UUID
    stripe_subscription_id: str
    stripe_item_id: str
    plan: str
    status: str
    current_period_end: datetime
    cancel_at_period_end: bool
    trial_end: datetime | None


async def select_subscription_by_org(
    conn: Connection,
    organization_id: UUID,
) -> SubscriptionByOrg | None:
    query = """
    SELECT subscription_id, stripe_subscription_id, stripe_item_id, plan, status,
           current_period_end, cancel_at_period_end, trial_end
    FROM subscriptions
    WHERE organization_id = $1
      AND is_deleted = FALSE
    ORDER BY
      CASE WHEN status IN ('canceled', 'incomplete_expired') THEN 1 ELSE 0 END,
      updated_at DESC,
      created_at DESC
    LIMIT 1
    """

    row = await conn.fetchrow(query, organization_id)

    if row is None:
        return None

    return SubscriptionByOrg(
        subscription_id=row["subscription_id"],
        stripe_subscription_id=row["stripe_subscription_id"],
        stripe_item_id=row["stripe_item_id"],
        plan=row["plan"],
        status=row["status"],
        current_period_end=row["current_period_end"],
        cancel_at_period_end=row["cancel_at_period_end"],
        trial_end=row["trial_end"],
    )
