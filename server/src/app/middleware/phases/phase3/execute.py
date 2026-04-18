from fastapi import HTTPException
from redis.asyncio import Redis
from starlette.requests import Request

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.logging.logger_setup import get_logger
from server.src.app.middleware.phases.phase1.request_context import RequestContext
from server.src.store.cache.idempotency import check_and_set_idempotency, hash_payload

logger = get_logger(__name__)

async def execute_phase_3(ctx: RequestContext, cache: Redis, lua_manager: LuaScriptManager, request: Request) -> RequestContext:
    if ctx.endpoint_config is None:
        return ctx

    if not ctx.endpoint_config.idempotency:
        return ctx

    if not ctx.idempotency_key:
        raise HTTPException(status_code=400, detail="MISSING_IDEMPOTENCY_KEY")

    body = await request.body()
    payload_hash = hash_payload(body)
    result = await check_and_set_idempotency(cache, lua_manager, ctx.idempotency_key, payload_hash)

    if not result.is_new:
        if result.stored_hash != payload_hash:
            logger.warning(
                "idempotency_payload_mismatch",
                extra={"key_hash": hash_blake2s(ctx.idempotency_key, digest_size=5), "path": ctx.route_template, "method": ctx.method},
            )
            raise HTTPException(status_code=409, detail="IDEMPOTENCY_KEY_PAYLOAD_MISMATCH")
        logger.warning(
            "duplicate_request",
            extra={"key_hash": hash_blake2s(ctx.idempotency_key, digest_size=5), "path": ctx.route_template, "method": ctx.method},
        )
        raise HTTPException(status_code=200, detail="DUPLICATE_ACCEPTED_PROCESSING")

    ctx.idempotency_lock_acquired = True
    return ctx