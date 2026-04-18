import asyncio

from fastapi import FastAPI
import httpx
from redis.asyncio import Redis

from server.src.app.crons.refresh_cloudflare_ips import cloudflare_ip_refresh_cron
from server.src.logic.workers.api_key_cache_invalidation_listener import api_key_cache_invalidation_listener
from server.src.logic.workers.handle_dummy_email import handle_dummy_email
from server.src.logic.workers.handle_email import handle_email_event
from server.src.logic.workers.handle_redis_session_expire import handle_device_sessions_expire, handle_session_expire, handle_session_hash_expire, handle_user_sessions_expire, handle_user_sessions_expire_except
from server.src.logic.workers.org_role_cache_invalidation_listener import org_role_cache_invalidation_listener
from server.src.logic.workers.session_memory_invalidation_listener import session_memory_invalidation_listener
from server.src.logic.workers.worker_event_loop import run_worker_loop

def start_background_workers(app: FastAPI, redis: Redis, http: httpx.AsyncClient, concurrency: int = 3) -> list[asyncio.Task]:
    lua_manager = app.state.lua_manager
    handlers = {
        "SEND_EMAIL_MESSAGE": lambda payload: handle_email_event(http, payload),
        "DUMMY_EMAIL": lambda payload: handle_dummy_email(payload),
        "SESSION_EXPIRE_FAILED": lambda payload: handle_session_expire(redis, lua_manager, payload),
        "SESSION_HASH_EXPIRE_FAILED": lambda payload: handle_session_hash_expire(redis, lua_manager, payload),
        "USER_SESSIONS_EXPIRE_FAILED": lambda payload: handle_user_sessions_expire(redis, lua_manager, payload),
        "USER_SESSIONS_EXPIRE_EXCEPT_FAILED": lambda payload: handle_user_sessions_expire_except(redis, lua_manager, payload),
        "DEVICE_SESSIONS_EXPIRE_FAILED": lambda payload: handle_device_sessions_expire(redis, lua_manager, payload),
    }

    tasks: list[asyncio.Task] = []

    for _ in range(concurrency):
        tasks.append(asyncio.create_task(run_worker_loop(redis, handlers)))

    tasks.append(asyncio.create_task(cloudflare_ip_refresh_cron(app, http)))
    tasks.append(asyncio.create_task(session_memory_invalidation_listener(redis, app.state.session_cache)))
    tasks.append(asyncio.create_task(org_role_cache_invalidation_listener(redis, app.state.org_role_cache)))
    tasks.append(asyncio.create_task(api_key_cache_invalidation_listener(redis, app.state.org_api_key_cache)))

    return tasks
