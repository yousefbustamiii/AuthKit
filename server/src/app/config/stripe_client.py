import stripe
from stripe import StripeClient

from server.src.app.config.settings import settings

_client = StripeClient(
    api_key=settings.stripe.secret_key,
    stripe_version="2026-03-25.dahlia",
)

async def create_stripe_customer(
    email: str,
    name: str | None = None,
    org_id: str | None = None,
) -> stripe.Customer:
    params: dict = {"email": email}
    if name:
        params["name"] = name
    if org_id:
        params["metadata"] = {"org_id": org_id}
    return await _client.customers.create_async(params)

async def create_stripe_checkout_session(
    customer_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
    org_id: str,
) -> stripe.checkout.Session:
    return await _client.checkout.sessions.create_async({
        "customer": customer_id,
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "subscription_data": {"metadata": {"org_id": org_id}},
    })

async def retrieve_stripe_subscription(subscription_id: str) -> stripe.Subscription:
    return await _client.subscriptions.retrieve_async(subscription_id)

async def cancel_stripe_subscription(
    subscription_id: str,
    *,
    at_period_end: bool = True,
) -> stripe.Subscription:
    if at_period_end:
        return await _client.subscriptions.update_async(
            subscription_id,
            {"cancel_at_period_end": True},
        )
    return await _client.subscriptions.cancel_async(subscription_id)

async def modify_stripe_subscription(
    subscription_id: str,
    item_id: str,
    new_price_id: str,
    *,
    proration_behavior: str = "always_invoice",
) -> stripe.Subscription:
    return await _client.subscriptions.update_async(
        subscription_id,
        {
            "items": [{"id": item_id, "price": new_price_id}],
            "proration_behavior": proration_behavior,
        },
    )

def construct_stripe_event(payload: bytes, sig_header: str) -> stripe.Event:
    try:
        return _client.construct_event(
            payload, sig_header, settings.stripe.webhook_secret
        )
    except stripe.SignatureVerificationError as e:
        raise ValueError("invalid_signature") from e
