from server.src.app.config.settings import settings

PLAN_PRICE_MAP: dict[int, str] = {
    1: settings.stripe.price_id_plan_1,
    2: settings.stripe.price_id_plan_2,
    3: settings.stripe.price_id_plan_3,
}

PRICE_PLAN_MAP: dict[str, str] = {v: f"plan_{k}" for k, v in PLAN_PRICE_MAP.items()}
