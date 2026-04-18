import secrets

def generate_event_token():
    return str("event_" + secrets.token_urlsafe(48))