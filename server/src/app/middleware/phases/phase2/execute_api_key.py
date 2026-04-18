from asyncpg import Pool
from cachetools import TTLCache
from fastapi import HTTPException
from redis.asyncio import Redis

from server.src.app.crypto.encryption.hash_blake2s import hash_blake2s
from server.src.app.logging.logger_setup import get_logger
from server.src.app.middleware.phases.phase1.request_context import RequestContext
from server.src.store.sql.core.api_keys.shared.resolve_api_key_by_hash import resolve_api_key_by_hash

logger = get_logger(__name__)

async def execute_phase_2_api_key(
    ctx: RequestContext,
    pool: Pool,
    cache: Redis,
    org_api_key_cache: TTLCache,
) -> RequestContext:
    if ctx.endpoint_config is None:
        return ctx

    access = ctx.endpoint_config.access
    if access not in ("api_key", "hybrid"):
        return ctx

    if access == "hybrid" and ctx.user_id is not None:
        return ctx

    if not ctx.api_key_token:
        logger.warning("missing_api_key", extra={"path": ctx.route_template, "method": ctx.method})
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    key_hash = hash_blake2s(ctx.api_key_token)
    api_key = await resolve_api_key_by_hash(cache, pool, key_hash, org_api_key_cache)

    if api_key is None:
        logger.warning("invalid_api_key", extra={"path": ctx.route_template, "method": ctx.method})
        raise HTTPException(status_code=401, detail="INVALID_API_KEY")

    ctx.key_id = api_key.key_id
    ctx.org_id = api_key.org_id
    ctx.project_id = api_key.project_id
    ctx.plan = api_key.plan

    return ctx
