import secrets

def generate_device_token():
    return str("device_" + secrets.token_urlsafe(48))