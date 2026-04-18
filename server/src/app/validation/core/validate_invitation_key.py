import re

INVITATION_KEY_RE = re.compile(
    r'^[ABCDEFGHJKLMNPQRSTUVWXYZ23456789]{4}'
    r'-[ABCDEFGHJKLMNPQRSTUVWXYZ23456789]{4}'
    r'-[ABCDEFGHJKLMNPQRSTUVWXYZ23456789]{4}$'
)

def validate_invitation_key(key: str) -> tuple[bool, str]:
    if not key or not isinstance(key, str):
        return False, "INVALID_KEY"
    key = key.strip().upper()
    if not INVITATION_KEY_RE.match(key):
        return False, "INVALID_FORMAT"
    return True, key
