from dataclasses import dataclass

from redis.asyncio import Redis

from server.src.app.config.github_http import initiate_github_oauth
from server.src.app.crypto.tokens.oauth_state_token import generate_oauth_state_token
from server.src.store.cache.authentication.oauth_state import store_oauth_state

@dataclass
class InitiateGithubOAuthResult:
    redirect_url: str

async def initiate_github_oauth_logic(cache: Redis) -> InitiateGithubOAuthResult:
    state = generate_oauth_state_token()
    await store_oauth_state(cache, state)
    redirect_url = initiate_github_oauth(state)
    return InitiateGithubOAuthResult(redirect_url=redirect_url)
