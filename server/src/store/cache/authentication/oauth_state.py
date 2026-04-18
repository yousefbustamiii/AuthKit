from redis.asyncio import Redis

from server.src.app.config.lua_manager import LuaScriptManager

async def store_oauth_state(cache: Redis, state: str) -> None:
    await cache.setex(f"oauth:state:{state}", 600, "1")

async def verify_and_consume_oauth_state(cache: Redis, lua_manager: LuaScriptManager, state: str) -> bool:
    result = await lua_manager.execute("authentication/oauth_state", [f"oauth:state:{state}"], [])
    return bool(result)
