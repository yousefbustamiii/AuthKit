import secrets

def generate_session_token():
    return str("sess_" + secrets.token_urlsafe(48))