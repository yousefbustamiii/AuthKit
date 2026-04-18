from typing import Annotated
from uuid import UUID

from asyncpg import Pool
from cachetools import TTLCache
from fastapi import Depends, HTTPException
import httpx
from redis.asyncio import Redis
from starlette.requests import Request

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher

def get_psql_pool(request: Request) -> Pool:
    return request.app.state.psql_pool

def get_redis_client(request: Request) -> Redis:
    return request.app.state.redis

def get_lua_manager(request: Request) -> LuaScriptManager:
    return request.app.state.lua_manager

def get_event_publisher(request: Request) -> RedisEventPublisher:
    return request.app.state.event_publisher

def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

def get_current_user(request: Request) -> UUID:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return user_id

def get_current_session_token(request: Request) -> str:
    session_token = getattr(request.state, "session_token", None)
    if not session_token:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return session_token

def get_country(request: Request) -> str:
    return getattr(request.state, "country", "Unknown")

def get_device(request: Request) -> str:
    return getattr(request.state, "device", "Unknown")

def get_device_token(request: Request) -> str | None:
    token = request.cookies.get("X-Device-Token") or None
    if not token:
        token = request.headers.get("X-Device-Token") or None
    return token

def get_os(request: Request) -> str:
    return getattr(request.state, "client_type", "web")

UserDep = Annotated[UUID, Depends(get_current_user)]
RedisDep = Annotated[Redis, Depends(get_redis_client)]
PoolDep = Annotated[Pool, Depends(get_psql_pool)]
HTTPDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]
SessionTokenDep = Annotated[str, Depends(get_current_session_token)]
CountryDep = Annotated[str, Depends(get_country)]
DeviceDep = Annotated[str, Depends(get_device)]
DeviceTokenDep = Annotated[str | None, Depends(get_device_token)]
LuaManagerDep = Annotated[LuaScriptManager, Depends(get_lua_manager)]
EventPublisherDep = Annotated[RedisEventPublisher, Depends(get_event_publisher)]
OsDep = Annotated[str, Depends(get_os)]

def get_org_role_cache(request: Request) -> TTLCache:
    return request.app.state.org_role_cache

OrgRoleCacheDep = Annotated[TTLCache, Depends(get_org_role_cache)]
