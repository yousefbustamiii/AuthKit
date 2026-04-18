from asyncpg import Pool
from cachetools import TTLCache
from fastapi import HTTPException
from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.logging.logger_setup import get_logger
from server.src.app.middleware.phases.phase1.request_context import RequestContext
from server.src.store.sql.authentication.sessions.shared.resolve_session_by_token_hash import resolve_session_by_token_hash

logger = get_logger(__name__)

async def execute_phase_2(
    ctx: RequestContext,
    pool: Pool,
    cache: Redis,
    session_cache: TTLCache,
    lua_manager: LuaScriptManager,
) -> RequestContext:
    if ctx.endpoint_config is None:
        return ctx

    access = ctx.endpoint_config.access

    if access in ("public", "api_key"):
        return ctx
    if access == "hybrid":
        if not ctx.session_token:
            return ctx
        session = await resolve_session_by_token_hash(cache, pool, ctx.session_token, session_cache, lua_manager)
        if session is None:
            logger.warning("invalid_session", extra={"path": ctx.route_template, "method": ctx.method})
            raise HTTPException(status_code=401, detail="INVALID_SESSION")
        ctx.user_id = session.user_id
        return ctx

    # "authenticated" — session token required
    if not ctx.session_token:
        logger.warning("missing_session_token", extra={"path": ctx.route_template, "method": ctx.method})
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    session = await resolve_session_by_token_hash(cache, pool, ctx.session_token, session_cache, lua_manager)

    if session is None:
        logger.warning("invalid_session", extra={"path": ctx.route_template, "method": ctx.method})
        raise HTTPException(status_code=401, detail="INVALID_SESSION")

    ctx.user_id = session.user_id

    return ctx
