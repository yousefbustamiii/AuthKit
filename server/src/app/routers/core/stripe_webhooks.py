from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

from server.src.app.config.stripe_client import construct_stripe_event
from server.src.app.logging.logger_setup import get_logger
from server.src.app.routers.dependencies.router_dependencies import PoolDep, RedisDep
from server.src.logic.core.billing.webhooks.handle_checkout_session_completed import handle_checkout_session_completed
from server.src.logic.core.billing.webhooks.handle_invoice_paid import handle_invoice_paid
from server.src.logic.core.billing.webhooks.handle_invoice_payment_action_required import handle_invoice_payment_action_required
from server.src.logic.core.billing.webhooks.handle_invoice_payment_failed import handle_invoice_payment_failed
from server.src.logic.core.billing.webhooks.handle_invoice_status_updated import handle_invoice_status_updated
from server.src.logic.core.billing.webhooks.handle_subscription_deleted import handle_subscription_deleted
from server.src.logic.core.billing.webhooks.handle_subscription_paused import handle_subscription_paused
from server.src.logic.core.billing.webhooks.handle_subscription_resumed import handle_subscription_resumed
from server.src.logic.core.billing.webhooks.handle_subscription_updated import handle_subscription_updated
from server.src.logic.core.billing.webhooks.handle_trial_will_end import handle_trial_will_end
from server.src.logic.core.billing.webhooks.idempotency import release_event_claim, try_claim_event

logger = get_logger(__name__)

router = APIRouter(prefix="/v1", default_response_class=ORJSONResponse)

@router.post("/core/billing/stripe")
async def stripe_webhook(request: Request, pool: PoolDep, cache: RedisDep):
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        return ORJSONResponse(status_code=400, content={"error": "missing_signature"})

    payload = await request.body()

    try:
        event = construct_stripe_event(payload, sig_header)
    except ValueError:
        return ORJSONResponse(status_code=400, content={"error": "invalid_signature"})

    event_id: str = event["id"]
    event_type: str = event["type"]
    data_obj: dict = event["data"]["object"]

    if not await try_claim_event(cache, event_id):
        return {"received": True}

    try:
        match event_type:
            case "checkout.session.completed":
                await handle_checkout_session_completed(pool, cache, data_obj)
            case "customer.subscription.updated":
                await handle_subscription_updated(pool, data_obj)
            case "customer.subscription.deleted":
                await handle_subscription_deleted(pool, cache, data_obj)
            case "customer.subscription.paused":
                await handle_subscription_paused(pool, cache, data_obj)
            case "customer.subscription.resumed":
                await handle_subscription_resumed(pool, cache, data_obj)
            case "customer.subscription.trial_will_end":
                await handle_trial_will_end(pool, cache, data_obj)
            case "invoice.paid":
                if not data_obj.get("hosted_invoice_url"):
                    logger.warning(
                        "invoice.paid received without hosted_invoice_url [event_id=%s]",
                        event_id,
                    )
                await handle_invoice_paid(pool, cache, data_obj)
            case "invoice.payment_failed":
                await handle_invoice_payment_failed(pool, cache, data_obj)
            case "invoice.payment_action_required":
                await handle_invoice_payment_action_required(pool, cache, data_obj)
            case "invoice.voided" | "invoice.marked_uncollectible":
                await handle_invoice_status_updated(pool, data_obj)
    except Exception:
        logger.exception("Stripe webhook handler failed [event_id=%s event_type=%s]", event_id, event_type)
        await release_event_claim(cache, event_id)
        return ORJSONResponse(status_code=500, content={"error": "handler_failed"})

    return {"received": True}