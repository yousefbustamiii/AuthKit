from dataclasses import dataclass
from datetime import datetime, timezone

from asyncpg import Pool
import httpx
from redis.asyncio import Redis

from server.src.app.config.email_templates import OAuthWelcomeTemplate
from server.src.app.config.google_http import exchange_google_code, get_google_userinfo
from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.errors.domains.authentication_errors import OAuthEmailNotVerifiedError, OAuthProviderError, OAuthStateMismatchError
from server.src.app.events.event_emitter import event_emitter
from server.src.app.events.pubsub.event_publisher import RedisEventPublisher
from server.src.app.logging.logger_setup import get_logger
from server.src.app.validation.validate_email import validate_email
from server.src.logic.authentication.shared.bootstrap_new_user import bootstrap_new_user
from server.src.logic.authentication.login.oauth.identity import lookup_oauth_identity
from server.src.logic.authentication.shared.issue_session import issue_session
from server.src.store.cache.authentication.expire_redis_session_by_hash import expire_redis_session_by_hash
from server.src.store.cache.authentication.oauth_state import verify_and_consume_oauth_state
from server.src.store.cache.authentication.set_redis_session import set_redis_session

logger = get_logger(__name__)

@dataclass
class OAuthCompleteResult:
    session_token: str
    expires_at: datetime
    device_token: str | None = None

async def complete_google_oauth(
    pool: Pool,
    cache: Redis,
    lua_manager: LuaScriptManager,
    http: httpx.AsyncClient,
    code: str,
    state: str,
    country: str,
    device: str,
    publisher: RedisEventPublisher,
) -> OAuthCompleteResult:
    state_valid = await verify_and_consume_oauth_state(cache, lua_manager, state)
    if not state_valid:
        raise OAuthStateMismatchError()

    try:
        access_token = await exchange_google_code(http, code)
        userinfo = await get_google_userinfo(http, access_token)
    except httpx.HTTPStatusError as exc:
        logger.warning("Google OAuth provider error: status=%s", exc.response.status_code)
        raise OAuthProviderError() from exc
    except Exception as exc:
        logger.warning("Google OAuth unexpected error: %s", type(exc).__name__)
        raise OAuthProviderError() from exc

    if not userinfo.get("email_verified"):
        raise OAuthEmailNotVerifiedError()

    raw_email: str = userinfo["email"]
    name: str | None = userinfo.get("given_name")
    avatar_url: str | None = userinfo.get("picture")
    
    is_valid_email, email_result = validate_email(raw_email)
    if not is_valid_email:
        raise OAuthProviderError()
    normalized_email: str = email_result

    async with pool.acquire() as conn:
        existing = await lookup_oauth_identity(conn, normalized_email)

        async with conn.transaction():
            if existing is not None:
                session = await issue_session(conn, existing.user_id, country, device)
                session_user_id = existing.user_id
                device_token = None
                recipient_email = existing.email
            else:
                bootstrap = await bootstrap_new_user(
                    conn,
                    email=normalized_email,
                    provider="google",
                    country=country,
                    device=device,
                    name=name,
                    avatar_url=avatar_url
                )
                session = bootstrap.session
                session_user_id = bootstrap.user_id
                device_token = bootstrap.device_token
                recipient_email = bootstrap.email

    await set_redis_session(cache, lua_manager, session.session_token, session.session_id, session_user_id, session.expires_at, device_id=session.device_id)
    if session.killed_session_token_hash:
        await expire_redis_session_by_hash(cache, lua_manager, session.killed_session_token_hash)
        await publisher.publish(
            "session:invalidation",
            "EXPIRE_SINGLE_SESSION_MEMORY",
            {"session_token_hash": session.killed_session_token_hash},
        )

    timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    template = OAuthWelcomeTemplate(
        provider="Google",
        device=device,
        country=country,
        timestamp=timestamp,
    )
    await event_emitter(cache, "SEND_EMAIL_MESSAGE", {
        "email": recipient_email,
        "subject": template.subject,
        "message": template.html,
    })

    return OAuthCompleteResult(
        session_token=session.session_token,
        expires_at=session.expires_at,
        device_token=device_token,
    )
