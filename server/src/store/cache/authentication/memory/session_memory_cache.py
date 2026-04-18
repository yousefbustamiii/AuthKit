from uuid import UUID

from cachetools import TTLCache

from server.src.store.sql.authentication.sessions.select_session_by_token_hash import SessionByTokenHash

def get_memory_session(session_cache: TTLCache, session_token_hash: str) -> SessionByTokenHash | None:
    return session_cache.get(f"session:{session_token_hash}")

def set_memory_session(session_cache: TTLCache, session_token_hash: str, session: SessionByTokenHash) -> None:
    session_cache[f"session:{session_token_hash}"] = session

def delete_memory_session(session_cache: TTLCache, session_token_hash: str) -> None:
    session_cache.pop(f"session:{session_token_hash}", None)

def delete_memory_sessions_by_user(session_cache: TTLCache, user_id: UUID) -> None:
    keys_to_delete = [k for k, v in list(session_cache.items()) if v.user_id == user_id]
    for key in keys_to_delete:
        session_cache.pop(key, None)

def delete_memory_sessions_by_devices(session_cache: TTLCache, device_ids: set[UUID]) -> None:
    keys_to_delete = [k for k, v in list(session_cache.items()) if v.device_id in device_ids]
    for key in keys_to_delete:
        session_cache.pop(key, None)

def delete_memory_sessions_by_user_except(session_cache: TTLCache, user_id: UUID, session_token_hash_to_keep: str) -> None:
    key_to_keep = f"session:{session_token_hash_to_keep}"
    keys_to_delete = [k for k, v in list(session_cache.items()) if v.user_id == user_id and k != key_to_keep]
    for key in keys_to_delete:
        session_cache.pop(key, None)
