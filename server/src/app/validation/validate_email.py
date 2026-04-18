from pathlib import Path
import re

BIN_FILE = (
    Path(__file__).parent  # validation/
    .parent                 # app/
    .parent                 # src/
    .parent                 # server/
    / "data"
    / "disposable_emails.bin"
)

DISPOSABLE_DOMAINS: frozenset[str] = frozenset(
    line.strip().lower()
    for line in BIN_FILE.read_text(encoding="utf-8").splitlines()
    if line.strip()
)

MAX_EMAIL_LEN  = 254
MAX_LOCAL_LEN  = 64
MAX_DOMAIN_LEN = 253
MAX_LABEL_LEN  = 63

EMAIL_RE = re.compile(
    r"^[a-z0-9._%+\-]{1,64}"
    r"@"
    r"(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)"
    r"+[a-z]{2,}$"
)

def validate_email(email: str) -> tuple[bool, str]:
    if not email or not isinstance(email, str):
        return False, "INVALID_EMAIL"

    email = email.strip().lower()
    if len(email) > MAX_EMAIL_LEN:
        return False, "EMAIL_TOO_LONG"
    if not EMAIL_RE.match(email):
        return False, "INVALID_FORMAT"
    local, domain = email.rsplit("@", 1)
    if len(local) > MAX_LOCAL_LEN:
        return False, "LOCAL_TOO_LONG"
    if len(domain) > MAX_DOMAIN_LEN:
        return False, "INVALID_FORMAT"
    if any(len(label) > MAX_LABEL_LEN for label in domain.split(".")):
        return False, "INVALID_FORMAT"
    if ".." in email:
        return False, "INVALID_FORMAT"
    if local.startswith(".") or local.endswith("."):
        return False, "INVALID_FORMAT"
    if domain in DISPOSABLE_DOMAINS:
        return False, "DISPOSABLE_EMAIL"
    return True, email
