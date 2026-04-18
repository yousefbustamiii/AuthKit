import re

MIN_NAME_LEN = 2
MAX_NAME_LEN = 64

LEADING_TRAILING_SPECIAL = re.compile(r'^[\s\-_.]|[\s\-_.]$')
CONSECUTIVE_SPECIAL      = re.compile(r'[\-_.]{2,}')
ALLOWED_CHARS            = re.compile(r'^[a-zA-Z0-9\s\-_.\'&]+$')

def validate_org_name(name: str) -> tuple[bool, str]:
    if not name or not isinstance(name, str):
        return False, "INVALID_NAME"
    name = name.strip()
    if not MIN_NAME_LEN <= len(name) <= MAX_NAME_LEN:
        return False, "INVALID_LENGTH"
    if not ALLOWED_CHARS.match(name):
        return False, "INVALID_CHARS"
    if LEADING_TRAILING_SPECIAL.search(name):
        return False, "INVALID_FORMAT"
    if CONSECUTIVE_SPECIAL.search(name):
        return False, "INVALID_FORMAT"
    if not re.search(r'[a-zA-Z]', name):
        return False, "NEEDS_LETTER"
    return True, name

def validate_project_name(name: str) -> tuple[bool, str]:
    if not name or not isinstance(name, str):
        return False, "INVALID_NAME"
    name = name.strip()
    if not MIN_NAME_LEN <= len(name) <= MAX_NAME_LEN:
        return False, "INVALID_LENGTH"
    if not ALLOWED_CHARS.match(name):
        return False, "INVALID_CHARS"
    if LEADING_TRAILING_SPECIAL.search(name):
        return False, "INVALID_FORMAT"
    if CONSECUTIVE_SPECIAL.search(name):
        return False, "INVALID_FORMAT"
    if not re.search(r'[a-zA-Z]', name):
        return False, "NEEDS_LETTER"
    return True, name

def validate_api_key_name(name: str) -> tuple[bool, str]:
    if not name or not isinstance(name, str):
        return False, "INVALID_NAME"
    name = name.strip()
    if not MIN_NAME_LEN <= len(name) <= MAX_NAME_LEN:
        return False, "INVALID_LENGTH"
    if not ALLOWED_CHARS.match(name):
        return False, "INVALID_CHARS"
    if LEADING_TRAILING_SPECIAL.search(name):
        return False, "INVALID_FORMAT"
    if CONSECUTIVE_SPECIAL.search(name):
        return False, "INVALID_FORMAT"
    if not re.search(r'[a-zA-Z]', name):
        return False, "NEEDS_LETTER"
    return True, name
