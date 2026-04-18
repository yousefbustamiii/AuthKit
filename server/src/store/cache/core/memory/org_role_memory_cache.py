from uuid import UUID

from cachetools import TTLCache

from server.src.store.sql.core.organizations.select_user_role_in_org import UserRoleInOrg

def get_memory_org_role(org_role_cache: TTLCache, organization_id: UUID, user_id: UUID) -> UserRoleInOrg | None:
    return org_role_cache.get(f"org_role:{organization_id}:{user_id}")

def set_memory_org_role(org_role_cache: TTLCache, organization_id: UUID, user_id: UUID, role_info: UserRoleInOrg) -> None:
    org_role_cache[f"org_role:{organization_id}:{user_id}"] = role_info

def delete_memory_org_role(org_role_cache: TTLCache, organization_id: UUID, user_id: UUID) -> None:
    org_role_cache.pop(f"org_role:{organization_id}:{user_id}", None)

def delete_all_memory_org_roles_for_user(org_role_cache: TTLCache, user_id: UUID) -> None:
    suffix = f":{user_id}"
    keys_to_delete = [
        key for key in org_role_cache.keys()
        if isinstance(key, str) and key.endswith(suffix) and key.startswith("org_role:")
    ]
    for key in keys_to_delete:
        org_role_cache.pop(key, None)

def delete_all_memory_users_for_org_role(org_role_cache: TTLCache, organization_id: UUID) -> None:
    prefix = f"org_role:{organization_id}:"
    keys_to_delete = [
        key for key in org_role_cache.keys()
        if isinstance(key, str) and key.startswith(prefix)
    ]
    for key in keys_to_delete:
        org_role_cache.pop(key, None)
