import secrets

def generate_project_api_key() -> str:
    return "sk_" + secrets.token_urlsafe(48)
