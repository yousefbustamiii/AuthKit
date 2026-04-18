from asyncpg import Pool

from server.src.logic.core.billing.subscription.sync_subscription import sync_subscription

async def handle_subscription_updated(pool: Pool, data_obj: dict) -> None:
    async with pool.acquire() as conn:
        await sync_subscription(conn, data_obj)
