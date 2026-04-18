import asyncio

from passlib.context import CryptContext

from server.src.app.config.settings import settings

argon2_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=settings.argon.time_cost,
    argon2__memory_cost=settings.argon.memory_cost,
    argon2__parallelism=settings.argon.parallelism,
    argon2__hash_len=settings.argon.hash_len,
    argon2__salt_len=settings.argon.salt_len
)

async def hash_password(password: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, argon2_context.hash, password)

async def verify_password_hash(hash: str, password: str) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, argon2_context.verify, password, hash)
