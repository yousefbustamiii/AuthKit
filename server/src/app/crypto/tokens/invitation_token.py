import secrets

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def generate_invitation_token() -> str:
    def segment(n: int) -> str:
        return "".join(secrets.choice(ALPHABET) for _ in range(n))
    return f"{segment(4)}-{segment(4)}-{segment(4)}"
