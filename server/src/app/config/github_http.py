import asyncio
import urllib.parse

import httpx

from server.src.app.config.settings import settings

async def exchange_github_code(client: httpx.AsyncClient, code: str, state: str) -> str:
    payload = {
        "client_id": settings.github.client_id,
        "client_secret": settings.github.client_secret,
        "code": code,
        "redirect_uri": settings.github.redirect_uri,
        "state": state,
    }
    headers = {"Accept": "application/json"}
    response = await client.post(settings.github.token_url, data=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise ValueError(f"GitHub token exchange error: {data.get('error_description', data['error'])}")

    return data["access_token"]


async def get_github_user_profile(client: httpx.AsyncClient, access_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    # Parallel fetch for performance
    prof_task = client.get(settings.github.user_url, headers=headers)
    email_task = client.get(settings.github.user_emails_url, headers=headers)
    
    prof_resp, email_resp = await asyncio.gather(prof_task, email_task)
    
    prof_resp.raise_for_status()
    email_resp.raise_for_status()
    
    profile = prof_resp.json()
    emails = email_resp.json()
    
    verified_email = None
    for entry in emails:
        if entry.get("primary") and entry.get("verified"):
            verified_email = entry["email"]
            break
            
    if not verified_email:
        raise ValueError("No primary verified email found on this GitHub account.")
    
    return {
        "email": verified_email,
        "name": profile.get("name"),
        "avatar_url": profile.get("avatar_url"),
    }


def initiate_github_oauth(state: str) -> str:
    params = {
        "client_id": settings.github.client_id,
        "redirect_uri": settings.github.redirect_uri,
        "scope": settings.github.scopes,
        "state": state,
    }
    return f"{settings.github.auth_url}?{urllib.parse.urlencode(params)}"
