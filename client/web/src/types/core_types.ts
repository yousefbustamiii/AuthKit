export type OrganizationRole = 'owner' | 'admin' | 'member'

export interface OrganizationListItem {
  organization_id: string
  name: string
  owner_user_id: string
  current_user_role: OrganizationRole
  created_at: string
}

export interface OrganizationMember {
  organization_member_id: string
  user_id: string
  email: string
  name: string | null
  avatar_url: string | null
  role: OrganizationRole
  invited_by_user_id: string | null
  created_at: string
}

export interface OrganizationInvitation {
  invitation_id: string
  email: string
  role: Exclude<OrganizationRole, 'owner'>
  invited_by_user_id: string
  created_at: string
  expires_at: string
}

export interface OrganizationProject {
  project_id: string
  name: string
  created_by_user_id: string
  created_at: string
}

export interface ProjectApiKey {
  key_id: string
  name: string
  created_by_user_id: string
  created_at: string
  rotated_at: string | null
  last_used_at: string | null
}

export interface BillingCustomer {
  customer_id: string
  stripe_customer_id: string
}

export interface BillingSubscription {
  subscription_id: string
  stripe_subscription_id: string
  stripe_item_id: string
  plan: string
  status: string
  current_period_end: string
  cancel_at_period_end: boolean
  trial_end: string | null
}

export interface BillingInvoice {
  invoice_id: string
  stripe_invoice_id: string
  stripe_subscription_id: string | null
  amount: number
  currency: string
  status: string
  hosted_invoice_url: string | null
  created_at: string
  updated_at: string
}

export interface OrganizationBilling {
  customer: BillingCustomer | null
  subscription: BillingSubscription | null
  invoices: BillingInvoice[]
}

export interface OrganizationsResponse {
  success: boolean
  organizations: OrganizationListItem[]
}

export interface OrganizationMembersResponse {
  success: boolean
  members: OrganizationMember[]
}

export interface OrganizationInvitationsResponse {
  success: boolean
  invitations: OrganizationInvitation[]
}

export interface OrganizationProjectsResponse {
  success: boolean
  projects: OrganizationProject[]
}

export interface ProjectApiKeysResponse {
  success: boolean
  api_keys: ProjectApiKey[]
}

export interface OrganizationBillingResponse {
  success: boolean
  customer: BillingCustomer | null
  subscription: BillingSubscription | null
  invoices: BillingInvoice[]
}

export interface CreatedOrganizationResponse {
  success: boolean
  organization_id: string
  organization_member_id: string
}

export interface InvitationResponse {
  success: boolean
  invitation_id: string
}

export interface CreatedProjectResponse {
  success: boolean
  project_id: string
}

export interface CreatedApiKeyResponse {
  success: boolean
  key_id: string
  raw_key: string
}

export interface RotatedApiKeyResponse {
  success: boolean
  key_id: string
  raw_key: string
}

export interface InitiateOrgDeletionResponse {
  success: boolean
  organization_id: string
}
