import * as core_api from '@/api/core_api'
import { generate_idempotency_key } from '@/lib/idempotency'
import { use_core_store } from '@/store/core_store'
import type { OrganizationBilling } from '@/types/core_types'

export async function load_organizations(): Promise<void> {
  const result = await core_api.get_organizations()
  use_core_store.getState().set_organizations(result.organizations)
}

export async function load_organization_members(organization_id: string): Promise<void> {
  const result = await core_api.get_organization_members(organization_id)
  use_core_store.getState().set_members(organization_id, result.members)
}

export async function load_organization_invitations(organization_id: string): Promise<void> {
  const result = await core_api.get_organization_invitations(organization_id)
  use_core_store.getState().set_invitations(organization_id, result.invitations)
}

export async function load_organization_projects(organization_id: string): Promise<void> {
  const result = await core_api.get_organization_projects(organization_id)
  use_core_store.getState().set_projects(organization_id, result.projects)
}

export async function load_project_api_keys(organization_id: string, project_id: string): Promise<void> {
  const result = await core_api.get_project_api_keys(organization_id, project_id)
  use_core_store.getState().set_api_keys(project_id, result.api_keys)
}

export async function load_organization_billing(organization_id: string): Promise<OrganizationBilling> {
  const result = await core_api.get_organization_billing(organization_id)
  const billing = {
    customer: result.customer,
    subscription: result.subscription,
    invoices: result.invoices,
  }
  use_core_store.getState().set_billing(organization_id, billing)
  return billing
}

export async function create_organization(name: string): Promise<string> {
  const result = await core_api.create_organization({ name }, generate_idempotency_key())
  await load_organizations()
  return result.organization_id
}

export async function edit_organization(organization_id: string, name: string): Promise<void> {
  await core_api.edit_organization(organization_id, { name }, generate_idempotency_key())
  await load_organizations()
}

export async function initiate_organization_delete(organization_id: string): Promise<void> {
  await core_api.initiate_organization_delete(organization_id, generate_idempotency_key())
}

export async function complete_organization_delete(organization_id: string, otp: string): Promise<void> {
  await core_api.complete_organization_delete(organization_id, { otp }, generate_idempotency_key())
  use_core_store.getState().remove_organization(organization_id)
}

export async function resend_organization_delete_otp(organization_id: string): Promise<void> {
  await core_api.resend_organization_delete_otp(organization_id)
}

export async function leave_organization(organization_id: string): Promise<void> {
  await core_api.leave_organization(organization_id, generate_idempotency_key())
  use_core_store.getState().remove_organization(organization_id)
}

export async function transfer_organization(
  organization_id: string,
  target_user_id: string,
  organization_name: string,
): Promise<void> {
  await core_api.transfer_organization(
    organization_id,
    { target_user_id, organization_name },
    generate_idempotency_key(),
  )
  await Promise.all([
    load_organizations(),
    load_organization_members(organization_id),
  ])
}

export async function invite_member(
  organization_id: string,
  email: string,
  role: 'admin' | 'member',
): Promise<void> {
  await core_api.invite_organization_member(organization_id, { email, role }, generate_idempotency_key())
  await load_organization_invitations(organization_id)
}

export async function cancel_invitation(organization_id: string, invitation_id: string): Promise<void> {
  await core_api.cancel_organization_invitation(organization_id, invitation_id, generate_idempotency_key())
  await load_organization_invitations(organization_id)
}

export async function accept_invitation(invitation_key: string): Promise<void> {
  await core_api.accept_organization_invitation({ invitation_key }, generate_idempotency_key())
  await load_organizations()
}

export async function promote_member(organization_id: string, target_user_id: string): Promise<void> {
  await core_api.promote_organization_member(organization_id, target_user_id, generate_idempotency_key())
  await load_organization_members(organization_id)
}

export async function demote_member(organization_id: string, target_user_id: string): Promise<void> {
  await core_api.demote_organization_member(organization_id, target_user_id, generate_idempotency_key())
  await load_organization_members(organization_id)
}

export async function remove_member(organization_id: string, target_user_id: string): Promise<void> {
  await core_api.remove_organization_member(organization_id, target_user_id, generate_idempotency_key())
  await load_organization_members(organization_id)
}

export async function create_project(organization_id: string, name: string): Promise<void> {
  await core_api.create_project(organization_id, { name }, generate_idempotency_key())
  await load_organization_projects(organization_id)
}

export async function edit_project(organization_id: string, project_id: string, name: string): Promise<void> {
  await core_api.edit_project(organization_id, project_id, { name }, generate_idempotency_key())
  await load_organization_projects(organization_id)
}

export async function delete_project(
  organization_id: string,
  project_id: string,
  name_confirmation: string,
): Promise<void> {
  await core_api.delete_project(organization_id, project_id, { name_confirmation }, generate_idempotency_key())
  await load_organization_projects(organization_id)
}

export async function create_api_key(organization_id: string, project_id: string, name: string): Promise<string> {
  const result = await core_api.create_api_key(organization_id, project_id, { name }, generate_idempotency_key())
  await load_project_api_keys(organization_id, project_id)
  return result.raw_key
}

export async function revoke_api_key(
  organization_id: string,
  project_id: string,
  key_id: string,
  confirmation: string,
): Promise<void> {
  await core_api.revoke_api_key(
    organization_id,
    project_id,
    key_id,
    { confirmation },
    generate_idempotency_key(),
  )
  await load_project_api_keys(organization_id, project_id)
}

export async function rotate_api_key(
  organization_id: string,
  project_id: string,
  key_id: string,
  confirmation: string,
): Promise<string> {
  const result = await core_api.rotate_api_key(
    organization_id,
    project_id,
    key_id,
    { confirmation },
    generate_idempotency_key(),
  )
  await load_project_api_keys(organization_id, project_id)
  return result.raw_key
}

export async function start_checkout(organization_id: string, plan_number: number): Promise<string> {
  const result = await core_api.billing_checkout(organization_id, { plan_number }, generate_idempotency_key())
  return result.checkout_url
}

export async function cancel_billing(organization_id: string): Promise<void> {
  await core_api.billing_cancel(organization_id, generate_idempotency_key())
  await load_organization_billing(organization_id)
}

export async function upgrade_billing(organization_id: string, plan_number: number): Promise<void> {
  await core_api.billing_upgrade(organization_id, { plan_number }, generate_idempotency_key())
  await load_organization_billing(organization_id)
}
