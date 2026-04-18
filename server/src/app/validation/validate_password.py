import re

UPPER = re.compile(r'[A-Z]')
LOWER = re.compile(r'[a-z]')
DIGIT = re.compile(r'[0-9]')
SPECIAL = re.compile(r'[!@#$%^&*()\-_=+\[\]{}|;:,.<>?]')
REPEAT = re.compile(r'(.)\1{3,}')
SEQUENTIAL = re.compile(r'(1234|abcd|qwerty|password)', re.IGNORECASE)

def validate_password(password: str) -> tuple[bool, str]:
    if not password or not isinstance(password, str):
        return False, "INVALID_PASSWORD"
    if not 12 <= len(password) <= 128:
        return False, "INVALID_LENGTH"
    if not UPPER.search(password):
        return False, "NEEDS_UPPERCASE"
    if not LOWER.search(password):
        return False, "NEEDS_LOWERCASE"
    if not DIGIT.search(password):
        return False, "NEEDS_DIGIT"
    if not SPECIAL.search(password):
        return False, "NEEDS_SPECIAL"
    if REPEAT.search(password):
        return False, "NO_REPEATING"
    if SEQUENTIAL.search(password):
        return False, "NO_SEQUENTIAL"
    return True, "OK"
