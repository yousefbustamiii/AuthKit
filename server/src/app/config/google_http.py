import urllib.parse

import httpx

from server.src.app.config.settings import settings

async def exchange_google_code(client: httpx.AsyncClient, code: str) -> str:
    payload = {
        "code": code,
        "client_id": settings.google.client_id,
        "client_secret": settings.google.client_secret,
        "redirect_uri": settings.google.redirect_uri,
        "grant_type": "authorization_code",
    }
    response = await client.post(settings.google.token_url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]


async def get_google_userinfo(client: httpx.AsyncClient, access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get(settings.google.userinfo_url, headers=headers)
    response.raise_for_status()
    return response.json()


def initiate_google_oauth(state: str) -> str:
    params = {
        "client_id": settings.google.client_id,
        "redirect_uri": settings.google.redirect_uri,
        "response_type": "code",
        "scope": settings.google.scopes,
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{settings.google.auth_url}?{urllib.parse.urlencode(params)}"
