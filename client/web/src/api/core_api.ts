import { api_request } from './client'
import type { BaseResponse } from '@/types/api_types'
import type {
  CreatedApiKeyResponse,
  CreatedProjectResponse,
  CreatedOrganizationResponse,
  InitiateOrgDeletionResponse,
  InvitationResponse,
  OrganizationBillingResponse,
  OrganizationInvitationsResponse,
  OrganizationMembersResponse,
  OrganizationProjectsResponse,
  OrganizationsResponse,
  ProjectApiKeysResponse,
  RotatedApiKeyResponse,
} from '@/types/core_types'

const CORE = '/v1/core'

export async function get_organizations(): Promise<OrganizationsResponse> {
  return api_request<OrganizationsResponse>(`${CORE}/organizations`)
}

export async function get_organization_members(organization_id: string): Promise<OrganizationMembersResponse> {
  return api_request<OrganizationMembersResponse>(`${CORE}/organizations/${organization_id}/members`)
}

export async function get_organization_invitations(organization_id: string): Promise<OrganizationInvitationsResponse> {
  return api_request<OrganizationInvitationsResponse>(`${CORE}/organizations/${organization_id}/invitations`)
}

export async function get_organization_projects(organization_id: string): Promise<OrganizationProjectsResponse> {
  return api_request<OrganizationProjectsResponse>(`${CORE}/organizations/${organization_id}/projects`)
}

export async function get_project_api_keys(
  organization_id: string,
  project_id: string,
): Promise<ProjectApiKeysResponse> {
  return api_request<ProjectApiKeysResponse>(
    `${CORE}/organizations/${organization_id}/projects/${project_id}/api-keys`,
  )
}

export async function get_organization_billing(organization_id: string): Promise<OrganizationBillingResponse> {
  return api_request<OrganizationBillingResponse>(`${CORE}/organizations/${organization_id}/billing`)
}

export async function create_organization(body: { name: string }, idempotency_key: string): Promise<CreatedOrganizationResponse> {
  return api_request<CreatedOrganizationResponse>(`${CORE}/organizations`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function edit_organization(
  organization_id: string,
  body: { name: string },
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/edit`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function initiate_organization_delete(
  organization_id: string,
  idempotency_key: string,
): Promise<InitiateOrgDeletionResponse> {
  return api_request<InitiateOrgDeletionResponse>(`${CORE}/organizations/${organization_id}/delete/initiate`, {
    method: 'POST',
    body: {},
    idempotency_key,
  })
}

export async function complete_organization_delete(
  organization_id: string,
  body: { otp: string },
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/delete/complete`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function resend_organization_delete_otp(organization_id: string): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/delete/resend`, {
    method: 'POST',
  })
}

export async function leave_organization(organization_id: string, idempotency_key: string): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/leave`, {
    method: 'POST',
    body: {},
    idempotency_key,
  })
}

export async function transfer_organization(
  organization_id: string,
  body: { target_user_id: string; organization_name: string },
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/transfer`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function invite_organization_member(
  organization_id: string,
  body: { email: string; role: 'admin' | 'member' },
  idempotency_key: string,
): Promise<InvitationResponse> {
  return api_request<InvitationResponse>(`${CORE}/organizations/${organization_id}/invitations`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function cancel_organization_invitation(
  organization_id: string,
  invitation_id: string,
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/invitations/${invitation_id}/cancel`, {
    method: 'POST',
    body: {},
    idempotency_key,
  })
}

export async function accept_organization_invitation(
  body: { invitation_key: string },
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/invitations/accept`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function remove_organization_member(
  organization_id: string,
  target_user_id: string,
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/members/${target_user_id}/remove`, {
    method: 'POST',
    body: {},
    idempotency_key,
  })
}

export async function promote_organization_member(
  organization_id: string,
  target_user_id: string,
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/members/${target_user_id}/promote`, {
    method: 'POST',
    body: {},
    idempotency_key,
  })
}

export async function demote_organization_member(
  organization_id: string,
  target_user_id: string,
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/members/${target_user_id}/demote`, {
    method: 'POST',
    body: {},
    idempotency_key,
  })
}

export async function create_project(
  organization_id: string,
  body: { name: string },
  idempotency_key: string,
): Promise<CreatedProjectResponse> {
  return api_request<CreatedProjectResponse>(`${CORE}/organizations/${organization_id}/projects`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function edit_project(
  organization_id: string,
  project_id: string,
  body: { name: string },
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/projects/${project_id}/edit`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function delete_project(
  organization_id: string,
  project_id: string,
  body: { name_confirmation: string },
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/projects/${project_id}/delete`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function create_api_key(
  organization_id: string,
  project_id: string,
  body: { name: string },
  idempotency_key: string,
): Promise<CreatedApiKeyResponse> {
  return api_request<CreatedApiKeyResponse>(`${CORE}/organizations/${organization_id}/projects/${project_id}/api-keys`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function revoke_api_key(
  organization_id: string,
  project_id: string,
  key_id: string,
  body: { confirmation: string },
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/projects/${project_id}/api-keys/${key_id}/revoke`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function rotate_api_key(
  organization_id: string,
  project_id: string,
  key_id: string,
  body: { confirmation: string },
  idempotency_key: string,
): Promise<RotatedApiKeyResponse> {
  return api_request<RotatedApiKeyResponse>(`${CORE}/organizations/${organization_id}/projects/${project_id}/api-keys/${key_id}/rotate`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function billing_checkout(
  organization_id: string,
  body: { plan_number: number },
  idempotency_key: string,
): Promise<{ success: boolean; checkout_url: string }> {
  return api_request<{ success: boolean; checkout_url: string }>(`${CORE}/organizations/${organization_id}/billing/checkout`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function billing_cancel(organization_id: string, idempotency_key: string): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/billing/cancel`, {
    method: 'POST',
    idempotency_key,
  })
}

export async function billing_upgrade(
  organization_id: string,
  body: { plan_number: number },
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${CORE}/organizations/${organization_id}/billing/upgrade`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}
