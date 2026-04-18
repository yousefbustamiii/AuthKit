import type { AuthenticatedUser, UserProfileResponse, UserSessionItem, UserDeviceItem } from './api_types'
import type { OrganizationBilling, OrganizationInvitation, OrganizationListItem, OrganizationMember, OrganizationProject, ProjectApiKey } from './core_types'

export interface AuthStoreState {
  user: AuthenticatedUser | null
  is_authenticated: boolean
  is_loading: boolean
  set_user: (user: AuthenticatedUser | null) => void
  set_loading: (loading: boolean) => void
  clear: () => void
}

export interface DashboardStoreState {
  profile: UserProfileResponse | null
  sessions: UserSessionItem[]
  devices: UserDeviceItem[]
  set_profile: (profile: UserProfileResponse | null) => void
  set_sessions: (sessions: UserSessionItem[]) => void
  set_devices: (devices: UserDeviceItem[]) => void
}

export interface CoreStoreState {
  organizations: OrganizationListItem[]
  selected_organization_id: string | null
  members_by_org: Record<string, OrganizationMember[]>
  invitations_by_org: Record<string, OrganizationInvitation[]>
  projects_by_org: Record<string, OrganizationProject[]>
  api_keys_by_project: Record<string, ProjectApiKey[]>
  billing_by_org: Record<string, OrganizationBilling | null>
  set_organizations: (organizations: OrganizationListItem[]) => void
  set_selected_organization_id: (organization_id: string | null) => void
  set_members: (organization_id: string, members: OrganizationMember[]) => void
  set_invitations: (organization_id: string, invitations: OrganizationInvitation[]) => void
  set_projects: (organization_id: string, projects: OrganizationProject[]) => void
  set_api_keys: (project_id: string, api_keys: ProjectApiKey[]) => void
  set_billing: (organization_id: string, billing: OrganizationBilling | null) => void
  remove_organization: (organization_id: string) => void
  clear: () => void
}
