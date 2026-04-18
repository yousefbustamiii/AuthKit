import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvloop

from server.src.app.config.cache_manager import create_memory_cache
from server.src.app.config.cloudflare_ip_ranges import load_from_json, refresh_cloudflare_ips
from server.src.app.config.geoip_client import create_geoip_reader
from server.src.app.config.http_client import create_http_client
from server.src.app.config.redis_client import create_redis_client
from server.src.app.config.settings import settings
from server.src.app.config.storage_client import create_psql_pool
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.app.logging.logger_setup import get_logger
from server.src.app.start.lua import initialize_lua
from server.src.app.start.worker import start_background_workers

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Enforce uvloop at runtime
    current_loop = asyncio.get_running_loop()
    if not isinstance(current_loop, uvloop.Loop):
        error_msg = f"App MUST run with uvloop! Detected: {type(current_loop).__name__}."
        logger.fatal(error_msg)
        raise RuntimeError(error_msg)

    # Startup
    app.state.psql_pool = await create_psql_pool()
    app.state.redis = await create_redis_client()
    app.state.http_client = await create_http_client()
    app.state.geoip_reader = create_geoip_reader()
    
    # L1 caches
    app.state.session_cache = create_memory_cache(maxsize=25_000, ttl=120)
    app.state.rate_limit_cache = create_memory_cache(maxsize=15_000, ttl=15)
    app.state.org_role_cache = create_memory_cache(maxsize=25_000, ttl=120)
    app.state.org_api_key_cache = create_memory_cache(maxsize=10_000, ttl=300)
    app.state.api_key_rate_limit_cache = create_memory_cache(maxsize=10_000, ttl=30)

    # Pub/Sub
    app.state.event_publisher = RedisEventPublisher(app.state.redis)

    # Initialize and load Lua scripts
    await initialize_lua(app)

    if settings.cf_guard_enabled:
        cf_ranges = load_from_json()
        app.state.cf_ip_ranges = await refresh_cloudflare_ips(app.state.http_client, cf_ranges)
    else:
        app.state.cf_ip_ranges = []

    app.state.worker_tasks = start_background_workers(app, app.state.redis, app.state.http_client)

    yield

    # Shutdown
    for task in app.state.worker_tasks:
        task.cancel()

    await asyncio.gather(*app.state.worker_tasks, return_exceptions=True)

    await app.state.psql_pool.close()
    await app.state.redis.aclose()
    await app.state.http_client.aclose()
    app.state.geoip_reader.close()