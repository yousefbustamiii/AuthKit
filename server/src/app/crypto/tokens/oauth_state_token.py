import secrets

def generate_oauth_state_token() -> str:
    return "oauth_" + secrets.token_urlsafe(48)
