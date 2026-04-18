from dataclasses import dataclass

from redis.asyncio import Redis

from server.src.app.config.google_http import initiate_google_oauth
from server.src.app.crypto.tokens.oauth_state_token import generate_oauth_state_token
from server.src.store.cache.authentication.oauth_state import store_oauth_state

@dataclass
class InitiateGoogleOAuthResult:
    redirect_url: str

async def initiate_google_oauth_logic(cache: Redis) -> InitiateGoogleOAuthResult:
    state = generate_oauth_state_token()
    await store_oauth_state(cache, state)
    redirect_url = initiate_google_oauth(state)
    return InitiateGoogleOAuthResult(redirect_url=redirect_url)
