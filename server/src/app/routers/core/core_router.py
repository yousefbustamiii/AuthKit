from uuid import UUID

from fastapi import APIRouter

from server.src.app.routers.classes.base import BaseResponse
from server.src.app.routers.classes.billing_classes import CreateCheckoutSessionRequest, CreateCheckoutSessionResponse, UpgradePlanRequest
from server.src.app.routers.classes.core_classes import AcceptInvitationRequest, BillingCustomerItem, BillingInvoiceItem, BillingSubscriptionItem, CompleteOrgDeletionRequest, CreateApiKeyRequest, CreateOrganizationRequest, CreateProjectRequest, CreatedApiKeyResponse, CreatedOrganizationResponse, CreatedProjectResponse, DeleteProjectRequest, EditOrganizationRequest, EditProjectRequest, InitiateOrgDeletionResponse, InvitationResponse, InviteOrganizationMemberRequest, OrganizationBillingResponse, OrganizationInvitationItem, OrganizationInvitationsResponse, OrganizationListItem, OrganizationMemberItem, OrganizationMembersResponse, OrganizationProjectItem, OrganizationProjectsResponse, OrganizationsResponse, ProjectApiKeyItem, ProjectApiKeysResponse, RevokeApiKeyRequest, RotateApiKeyRequest, RotatedApiKeyResponse, TransferOrganizationRequest
from server.src.app.routers.dependencies.router_dependencies import CountryDep, DeviceDep, LuaManagerDep, OrgRoleCacheDep, PoolDep, RedisDep, UserDep
from server.src.logic.core.api_keys.ui.get_api_key_functions import get_project_api_keys_data
from server.src.logic.core.billing.ui.get_billing_functions import get_organization_billing_data
from server.src.logic.core.organizations.members.ui.get_organization_member_functions import get_organization_invitations_data, get_organization_members_data
from server.src.logic.core.organizations.ui.get_organization_functions import get_user_organizations_data
from server.src.logic.core.projects.ui.get_project_functions import get_organization_projects_data
from server.src.logic.core.api_keys.create_project_api_key import create_project_api_key
from server.src.logic.core.api_keys.revoke_project_api_key import revoke_project_api_key
from server.src.logic.core.api_keys.rotate_project_api_key import rotate_project_api_key
from server.src.logic.core.billing.subscription.cancel_subscription import cancel_subscription
from server.src.logic.core.billing.subscription.create_checkout_session import create_checkout_session
from server.src.logic.core.billing.subscription.upgrade_subscription import upgrade_subscription
from server.src.logic.core.organizations.complete_organization_deletion import complete_organization_deletion
from server.src.logic.core.organizations.create_organization import create_organization
from server.src.logic.core.organizations.edit_organization import edit_organization
from server.src.logic.core.organizations.initiate_organization_deletion import initiate_organization_deletion
from server.src.logic.core.organizations.leave_organization import leave_organization
from server.src.logic.core.organizations.resend_organization_deletion import resend_organization_deletion
from server.src.logic.core.organizations.members.invitations.accept_organization_invitation import accept_organization_invitation
from server.src.logic.core.organizations.members.invitations.cancel_organization_invitation import cancel_organization_invitation
from server.src.logic.core.organizations.members.invitations.invite_organization_member import invite_organization_member
from server.src.logic.core.organizations.members.remove_organization_member import remove_organization_member
from server.src.logic.core.organizations.members.roles.demote_organization_member import demote_organization_member
from server.src.logic.core.organizations.members.roles.promote_organization_member import promote_organization_member
from server.src.logic.core.organizations.transfer_organization_ownership import transfer_organization_ownership
from server.src.logic.core.projects.create_project import create_project
from server.src.logic.core.projects.delete_project import delete_project
from server.src.logic.core.projects.edit_project import edit_project

router = APIRouter(prefix="/v1")

# --- Core Reads ---

@router.get("/core/organizations", response_model=OrganizationsResponse)
async def org_list(pool: PoolDep, user_id: UserDep):
    organizations = await get_user_organizations_data(pool, user_id)
    return OrganizationsResponse(
        organizations=[
            OrganizationListItem(
                organization_id=o.organization_id,
                name=o.name,
                owner_user_id=o.owner_user_id,
                current_user_role=o.current_user_role,
                created_at=o.created_at,
            )
            for o in organizations
        ]
    )


@router.get("/core/organizations/{organization_id}/members", response_model=OrganizationMembersResponse)
async def org_members_list(organization_id: UUID, pool: PoolDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    members = await get_organization_members_data(pool, org_role_cache, user_id, organization_id)
    return OrganizationMembersResponse(
        members=[
            OrganizationMemberItem(
                organization_member_id=m.organization_member_id,
                user_id=m.user_id,
                email=m.email,
                name=m.name,
                avatar_url=m.avatar_url,
                role=m.role,
                invited_by_user_id=m.invited_by_user_id,
                created_at=m.created_at,
            )
            for m in members
        ]
    )


@router.get("/core/organizations/{organization_id}/invitations", response_model=OrganizationInvitationsResponse)
async def org_invitations_list(organization_id: UUID, pool: PoolDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    invitations = await get_organization_invitations_data(pool, org_role_cache, user_id, organization_id)
    return OrganizationInvitationsResponse(
        invitations=[
            OrganizationInvitationItem(
                invitation_id=i.invitation_id,
                email=i.email,
                role=i.role,
                invited_by_user_id=i.invited_by_user_id,
                created_at=i.created_at,
                expires_at=i.expires_at,
            )
            for i in invitations
        ]
    )


@router.get("/core/organizations/{organization_id}/projects", response_model=OrganizationProjectsResponse)
async def org_projects_list(organization_id: UUID, pool: PoolDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    projects = await get_organization_projects_data(pool, org_role_cache, user_id, organization_id)
    return OrganizationProjectsResponse(
        projects=[
            OrganizationProjectItem(
                project_id=p.project_id,
                name=p.name,
                created_by_user_id=p.created_by_user_id,
                created_at=p.created_at,
            )
            for p in projects
        ]
    )


@router.get("/core/organizations/{organization_id}/projects/{project_id}/api-keys", response_model=ProjectApiKeysResponse)
async def project_api_keys_list(organization_id: UUID, project_id: UUID, pool: PoolDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    api_keys = await get_project_api_keys_data(pool, org_role_cache, user_id, organization_id, project_id)
    return ProjectApiKeysResponse(
        api_keys=[
            ProjectApiKeyItem(
                key_id=k.key_id,
                name=k.name,
                created_by_user_id=k.created_by_user_id,
                created_at=k.created_at,
                rotated_at=k.rotated_at,
                last_used_at=k.last_used_at,
            )
            for k in api_keys
        ]
    )


@router.get("/core/organizations/{organization_id}/billing", response_model=OrganizationBillingResponse)
async def org_billing_get(organization_id: UUID, pool: PoolDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    billing = await get_organization_billing_data(pool, org_role_cache, user_id, organization_id)
    return OrganizationBillingResponse(
        customer=None if billing.customer is None else BillingCustomerItem(
            customer_id=billing.customer.customer_id,
            stripe_customer_id=billing.customer.stripe_customer_id,
        ),
        subscription=None if billing.subscription is None else BillingSubscriptionItem(
            subscription_id=billing.subscription.subscription_id,
            stripe_subscription_id=billing.subscription.stripe_subscription_id,
            stripe_item_id=billing.subscription.stripe_item_id,
            plan=billing.subscription.plan,
            status=billing.subscription.status,
            current_period_end=billing.subscription.current_period_end,
            cancel_at_period_end=billing.subscription.cancel_at_period_end,
            trial_end=billing.subscription.trial_end,
        ),
        invoices=[
            BillingInvoiceItem(
                invoice_id=i.invoice_id,
                stripe_invoice_id=i.stripe_invoice_id,
                stripe_subscription_id=i.stripe_subscription_id,
                amount=i.amount,
                currency=i.currency,
                status=i.status,
                hosted_invoice_url=i.hosted_invoice_url,
                created_at=i.created_at,
                updated_at=i.updated_at,
            )
            for i in billing.invoices
        ],
    )

# --- Organizations ---

@router.post("/core/organizations", response_model=CreatedOrganizationResponse)
async def org_create(body: CreateOrganizationRequest, pool: PoolDep, cache: RedisDep, user_id: UserDep):
    result = await create_organization(pool, cache, user_id, body.name)
    return CreatedOrganizationResponse(organization_id=result.organization_id, organization_member_id=result.organization_member_id)

@router.post("/core/organizations/{organization_id}/edit", response_model=BaseResponse)
async def org_edit(organization_id: UUID, body: EditOrganizationRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await edit_organization(pool, cache, org_role_cache, user_id, organization_id, body.name)
    return BaseResponse()

@router.post("/core/organizations/{organization_id}/delete/initiate", response_model=InitiateOrgDeletionResponse)
async def org_delete_initiate(organization_id: UUID, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep, country: CountryDep, device: DeviceDep):
    result = await initiate_organization_deletion(pool, cache, org_role_cache, user_id, organization_id, country, device)
    return InitiateOrgDeletionResponse(organization_id=result.organization_id)

@router.post("/core/organizations/{organization_id}/delete/complete", response_model=BaseResponse)
async def org_delete_complete(organization_id: UUID, body: CompleteOrgDeletionRequest, pool: PoolDep, cache: RedisDep, user_id: UserDep):
    await complete_organization_deletion(pool, cache, user_id, organization_id, body.otp)
    return BaseResponse()

@router.post("/core/organizations/{organization_id}/delete/resend", response_model=BaseResponse)
async def org_delete_resend(
    organization_id: UUID,
    pool: PoolDep,
    cache: RedisDep,
    lua_manager: LuaManagerDep,
    org_role_cache: OrgRoleCacheDep,
    user_id: UserDep,
    country: CountryDep,
    device: DeviceDep,
):
    await resend_organization_deletion(pool, cache, lua_manager, org_role_cache, user_id, organization_id, country, device)
    return BaseResponse()

@router.post("/core/organizations/{organization_id}/leave", response_model=BaseResponse)
async def org_leave(organization_id: UUID, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await leave_organization(pool, cache, org_role_cache, user_id, organization_id)
    return BaseResponse()

@router.post("/core/organizations/{organization_id}/transfer", response_model=BaseResponse)
async def org_transfer(organization_id: UUID, body: TransferOrganizationRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await transfer_organization_ownership(pool, cache, org_role_cache, user_id, organization_id, body.target_user_id, body.organization_name)
    return BaseResponse()

# --- Organization Members ---

@router.post("/core/organizations/{organization_id}/members/{target_user_id}/remove", response_model=BaseResponse)
async def org_member_remove(organization_id: UUID, target_user_id: UUID, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await remove_organization_member(pool, cache, org_role_cache, user_id, organization_id, target_user_id)
    return BaseResponse()

@router.post("/core/organizations/{organization_id}/members/{target_user_id}/promote", response_model=BaseResponse)
async def org_member_promote(organization_id: UUID, target_user_id: UUID, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await promote_organization_member(pool, cache, org_role_cache, user_id, organization_id, target_user_id)
    return BaseResponse()

@router.post("/core/organizations/{organization_id}/members/{target_user_id}/demote", response_model=BaseResponse)
async def org_member_demote(organization_id: UUID, target_user_id: UUID, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await demote_organization_member(pool, cache, org_role_cache, user_id, organization_id, target_user_id)
    return BaseResponse()

# --- Organization Invitations ---

@router.post("/core/organizations/{organization_id}/invitations", response_model=InvitationResponse)
async def org_invitation_create(organization_id: UUID, body: InviteOrganizationMemberRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    result = await invite_organization_member(pool, cache, org_role_cache, user_id, organization_id, body.email, body.role)
    return InvitationResponse(invitation_id=result.invitation_id)

@router.post("/core/organizations/{organization_id}/invitations/{invitation_id}/cancel", response_model=BaseResponse)
async def org_invitation_cancel(organization_id: UUID, invitation_id: UUID, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await cancel_organization_invitation(pool, cache, org_role_cache, user_id, organization_id, invitation_id)
    return BaseResponse()

@router.post("/core/organizations/invitations/accept", response_model=BaseResponse)
async def org_invitation_accept(body: AcceptInvitationRequest, pool: PoolDep, cache: RedisDep, user_id: UserDep):
    await accept_organization_invitation(pool, cache, user_id, body.invitation_key)
    return BaseResponse()

# --- Projects ---

@router.post("/core/organizations/{organization_id}/projects", response_model=CreatedProjectResponse)
async def project_create(organization_id: UUID, body: CreateProjectRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    result = await create_project(pool, cache, org_role_cache, user_id, organization_id, body.name)
    return CreatedProjectResponse(project_id=result.project_id)

@router.post("/core/organizations/{organization_id}/projects/{project_id}/edit", response_model=BaseResponse)
async def project_edit(organization_id: UUID, project_id: UUID, body: EditProjectRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await edit_project(pool, cache, org_role_cache, user_id, organization_id, project_id, body.name)
    return BaseResponse()

@router.post("/core/organizations/{organization_id}/projects/{project_id}/delete", response_model=BaseResponse)
async def project_delete(organization_id: UUID, project_id: UUID, body: DeleteProjectRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await delete_project(pool, cache, org_role_cache, user_id, organization_id, project_id, body.name_confirmation)
    return BaseResponse()

# --- API Keys ---

@router.post("/core/organizations/{organization_id}/projects/{project_id}/api-keys", response_model=CreatedApiKeyResponse)
async def api_key_create(organization_id: UUID, project_id: UUID, body: CreateApiKeyRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    result = await create_project_api_key(pool, cache, org_role_cache, user_id, organization_id, project_id, body.name)
    return CreatedApiKeyResponse(key_id=result.key_id, raw_key=result.raw_key)

@router.post("/core/organizations/{organization_id}/projects/{project_id}/api-keys/{key_id}/revoke", response_model=BaseResponse)
async def api_key_revoke(organization_id: UUID, project_id: UUID, key_id: UUID, body: RevokeApiKeyRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await revoke_project_api_key(pool, cache, org_role_cache, user_id, organization_id, project_id, key_id, body.confirmation)
    return BaseResponse()

@router.post("/core/organizations/{organization_id}/projects/{project_id}/api-keys/{key_id}/rotate", response_model=RotatedApiKeyResponse)
async def api_key_rotate(organization_id: UUID, project_id: UUID, key_id: UUID, body: RotateApiKeyRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    result = await rotate_project_api_key(pool, cache, org_role_cache, user_id, organization_id, project_id, key_id, body.confirmation)
    return RotatedApiKeyResponse(key_id=result.key_id, raw_key=result.raw_key)

# --- Billing ---

@router.post("/core/organizations/{organization_id}/billing/checkout", response_model=CreateCheckoutSessionResponse)
async def billing_checkout(organization_id: UUID, body: CreateCheckoutSessionRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    result = await create_checkout_session(pool, cache, org_role_cache, user_id, organization_id, body.plan_number)
    return CreateCheckoutSessionResponse(checkout_url=result.checkout_url)

@router.post("/core/organizations/{organization_id}/billing/cancel", response_model=BaseResponse)
async def billing_cancel(organization_id: UUID, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await cancel_subscription(pool, cache, org_role_cache, user_id, organization_id)
    return BaseResponse()

@router.post("/core/organizations/{organization_id}/billing/upgrade", response_model=BaseResponse)
async def billing_upgrade(organization_id: UUID, body: UpgradePlanRequest, pool: PoolDep, cache: RedisDep, org_role_cache: OrgRoleCacheDep, user_id: UserDep):
    await upgrade_subscription(pool, cache, org_role_cache, user_id, organization_id, body.plan_number)
    return BaseResponse()
