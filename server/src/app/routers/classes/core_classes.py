from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from server.src.app.routers.classes.base import BaseResponse

# --- Request Classes ---

class CreateOrganizationRequest(BaseModel):
    name: str

class EditOrganizationRequest(BaseModel):
    name: str

class CompleteOrgDeletionRequest(BaseModel):
    otp: str

class TransferOrganizationRequest(BaseModel):
    target_user_id: UUID
    organization_name: str

class InviteOrganizationMemberRequest(BaseModel):
    email: str
    role: str

class AcceptInvitationRequest(BaseModel):
    invitation_key: str

class CreateProjectRequest(BaseModel):
    name: str

class EditProjectRequest(BaseModel):
    name: str

class DeleteProjectRequest(BaseModel):
    name_confirmation: str

class CreateApiKeyRequest(BaseModel):
    name: str

class RevokeApiKeyRequest(BaseModel):
    confirmation: str

class RotateApiKeyRequest(BaseModel):
    confirmation: str

# --- Read Response Item Classes ---

class OrganizationListItem(BaseModel):
    organization_id: UUID
    name: str
    owner_user_id: UUID
    current_user_role: str
    created_at: datetime

class OrganizationMemberItem(BaseModel):
    organization_member_id: UUID
    user_id: UUID
    email: str
    name: str | None
    avatar_url: str | None
    role: str
    invited_by_user_id: UUID | None
    created_at: datetime

class OrganizationInvitationItem(BaseModel):
    invitation_id: UUID
    email: str
    role: str
    invited_by_user_id: UUID
    created_at: datetime
    expires_at: datetime

class OrganizationProjectItem(BaseModel):
    project_id: UUID
    name: str
    created_by_user_id: UUID
    created_at: datetime

class ProjectApiKeyItem(BaseModel):
    key_id: UUID
    name: str
    created_by_user_id: UUID
    created_at: datetime
    rotated_at: datetime | None
    last_used_at: datetime | None

class BillingCustomerItem(BaseModel):
    customer_id: UUID
    stripe_customer_id: str

class BillingSubscriptionItem(BaseModel):
    subscription_id: UUID
    stripe_subscription_id: str
    stripe_item_id: str
    plan: str
    status: str
    current_period_end: datetime
    cancel_at_period_end: bool
    trial_end: datetime | None

class BillingInvoiceItem(BaseModel):
    invoice_id: UUID
    stripe_invoice_id: str
    stripe_subscription_id: str | None
    amount: int
    currency: str
    status: str
    hosted_invoice_url: str | None
    created_at: datetime
    updated_at: datetime

# --- Response Classes ---

class CreatedOrganizationResponse(BaseResponse):
    organization_id: UUID
    organization_member_id: UUID

class InitiateOrgDeletionResponse(BaseResponse):
    organization_id: str

class InvitationResponse(BaseResponse):
    invitation_id: UUID

class CreatedProjectResponse(BaseResponse):
    project_id: UUID

class CreatedApiKeyResponse(BaseResponse):
    key_id: UUID
    raw_key: str

class RotatedApiKeyResponse(BaseResponse):
    key_id: UUID
    raw_key: str

class OrganizationsResponse(BaseResponse):
    organizations: list[OrganizationListItem]

class OrganizationMembersResponse(BaseResponse):
    members: list[OrganizationMemberItem]

class OrganizationInvitationsResponse(BaseResponse):
    invitations: list[OrganizationInvitationItem]

class OrganizationProjectsResponse(BaseResponse):
    projects: list[OrganizationProjectItem]

class ProjectApiKeysResponse(BaseResponse):
    api_keys: list[ProjectApiKeyItem]

class OrganizationBillingResponse(BaseResponse):
    customer: BillingCustomerItem | None
    subscription: BillingSubscriptionItem | None
    invoices: list[BillingInvoiceItem]
