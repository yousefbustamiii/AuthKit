import asyncpg

from server.src.app.config.settings import settings

async def create_psql_pool() -> asyncpg.Pool:
    pool = await asyncpg.create_pool(
        dsn=settings.psql_dsn,
        min_size=2,
        max_size=5,
        max_inactive_connection_lifetime=300,
        command_timeout=10,
        statement_cache_size=100,
        timeout=3
    )
    return pool