import secrets

def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"