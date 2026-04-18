from dataclasses import dataclass
from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from redis.asyncio import Redis

from server.src.app.config.settings import settings
from server.src.app.config.stripe_client import create_stripe_checkout_session, create_stripe_customer
from server.src.app.crypto.encryption.aes_decrypt import decrypt
from server.src.app.errors.domains.authentication_errors import UserNotFoundError
from server.src.app.errors.domains.billing_errors import InvalidPlanNumberError, SubscriptionAlreadyActiveError
from server.src.app.errors.domains.core_errors import OrgAccessDeniedError
from server.src.app.logging.logger_setup import get_logger
from server.src.logic.core.billing.subscription.plan_price_maps import PLAN_PRICE_MAP
from server.src.store.sql.authentication.users.select_user_by_id import select_user_by_id
from server.src.store.sql.core.billing.customers.insert_customer import insert_customer
from server.src.store.sql.core.billing.customers.select_customer_by_org import select_customer_by_org
from server.src.store.sql.core.billing.subscriptions.select_subscription_by_org import select_subscription_by_org
from server.src.store.sql.core.organizations.shared.resolve_user_role_in_org import resolve_user_role_in_org

logger = get_logger(__name__)

@dataclass
class CheckoutSessionResult:
    checkout_url: str

async def create_checkout_session(
    pool: Pool,
    cache: Redis,
    org_role_cache: TTLCache,
    user_id: UUID,
    organization_id: UUID,
    plan_number: int,
) -> CheckoutSessionResult:
    price_id = PLAN_PRICE_MAP.get(plan_number)
    if price_id is None:
        raise InvalidPlanNumberError()

    membership = await resolve_user_role_in_org(pool, organization_id, user_id, org_role_cache)
    if membership.role != "owner":
        raise OrgAccessDeniedError()

    async with pool.acquire() as conn:
        user = await select_user_by_id(conn, user_id)
        if user is None:
            raise UserNotFoundError()
        email = decrypt(user.email_encrypted)
        existing_sub = await select_subscription_by_org(conn, organization_id)
        if existing_sub is not None and existing_sub.status not in ("incomplete_expired", "canceled"):
            raise SubscriptionAlreadyActiveError()
        customer = await select_customer_by_org(conn, organization_id)

    if customer is not None:
        stripe_customer_id = customer.stripe_customer_id
    else:
        stripe_cust = await create_stripe_customer(email, org_id=str(organization_id))
        async with pool.acquire() as conn:
            inserted = await insert_customer(conn, user_id, organization_id, stripe_cust.id)
        if inserted.stripe_customer_id != stripe_cust.id:
            logger.warning(
                "Orphaned Stripe customer created due to concurrent checkout race "
                "[orphaned=%s winner=%s org_id=%s]",
                stripe_cust.id,
                inserted.stripe_customer_id,
                organization_id,
            )
        stripe_customer_id = inserted.stripe_customer_id

    session = await create_stripe_checkout_session(
        customer_id=stripe_customer_id,
        price_id=price_id,
        success_url=settings.stripe.success_url,
        cancel_url=settings.stripe.cancel_url,
        org_id=str(organization_id),
    )

    return CheckoutSessionResult(checkout_url=session.url)
