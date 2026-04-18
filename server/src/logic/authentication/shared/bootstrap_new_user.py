import re
from dataclasses import dataclass
from uuid import UUID

from asyncpg import Connection

from server.src.app.validation.core.validate_core_names import MAX_NAME_LEN, validate_org_name
from server.src.logic.authentication.shared.issue_session_with_device import IssuedSessionWithDevice, issue_session_with_device
from server.src.store.sql.authentication.users.insert_user import Provider, insert_user
from server.src.store.sql.core.organizations.insert_organization import insert_organization
from server.src.store.sql.core.organizations.members.insert_organization_member import insert_organization_member

ORG_NAME_SUFFIX = "'s Organization"
SAFE_ORG_CHAR = re.compile(r"[^a-zA-Z0-9\s\-_.\'&]+")
MULTISPACE = re.compile(r"\s+")
HAS_LETTER = re.compile(r"[a-zA-Z]")


@dataclass
class BootstrappedUser:
    user_id: UUID
    email: str
    device_token: str
    session: IssuedSessionWithDevice


def _normalize_org_name_source(value: str) -> str:
    cleaned = SAFE_ORG_CHAR.sub(" ", value)
    cleaned = MULTISPACE.sub(" ", cleaned).strip(" -_.")
    return cleaned


def derive_initial_organization_name(name: str | None, email: str) -> str:
    candidates = [name or "", email.split("@", 1)[0], email]
    max_base_len = MAX_NAME_LEN - len(ORG_NAME_SUFFIX)

    for source in candidates:
        cleaned = _normalize_org_name_source(source)
        if not cleaned or not HAS_LETTER.search(cleaned):
            continue

        cleaned = cleaned[:max_base_len].rstrip(" -_.")
        if not cleaned:
            continue

        ok, normalized = validate_org_name(f"{cleaned}{ORG_NAME_SUFFIX}")
        if ok:
            return normalized

    raise ValueError("Unable to derive a valid initial organization name.")


async def bootstrap_new_user(
    conn: Connection,
    *,
    email: str,
    provider: Provider,
    country: str,
    device: str,
    name: str | None = None,
    avatar_url: str | None = None,
    password_hash: str | None = None,
) -> BootstrappedUser:
    user = await insert_user(
        conn,
        email,
        provider=provider,
        password_hash=password_hash,
        name=name,
        avatar_url=avatar_url,
    )
    organization_name = derive_initial_organization_name(name, email)
    org = await insert_organization(conn, name=organization_name, owner_user_id=user.user_id)
    await insert_organization_member(conn, organization_id=org.organization_id, user_id=user.user_id)
    session = await issue_session_with_device(conn, user.user_id, country, device)

    return BootstrappedUser(
        user_id=user.user_id,
        email=email,
        device_token=session.device_token,
        session=session,
    )
