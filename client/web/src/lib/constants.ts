export const BASE_URL = 'https://authkit-b533.onrender.com'

export const ROUTES = {
  ROOT: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  OTP: '/auth/otp',
  PASSWORD_RESET: '/auth/password-reset',
  PASSWORD_RESET_VERIFY: '/auth/password-reset/verify',
  PASSWORD_RESET_COMPLETE: '/auth/password-reset/complete',
  OAUTH_GOOGLE_CALLBACK: '/auth/oauth/google/callback',
  OAUTH_GITHUB_CALLBACK: '/auth/oauth/github/callback',
  DASHBOARD: '/dashboard',
  DASHBOARD_ORGANIZATIONS: '/dashboard/organizations',
  DASHBOARD_INVITATIONS_ACCEPT: '/dashboard/invitations/accept',
  DASHBOARD_PROFILE: '/dashboard/profile',
  DASHBOARD_DEVICES: '/dashboard/devices',
  DASHBOARD_SETTINGS_EMAIL: '/dashboard/settings/email',
  DASHBOARD_SETTINGS_PASSWORD: '/dashboard/settings/password',
  DASHBOARD_SETTINGS_DELETE: '/dashboard/settings/delete',
  BILLING_SUCCESS: '/billing/success',
  BILLING_CANCEL: '/billing/cancel',
} as const

export const core_routes = {
  organization_members: (organization_id: string) => `/dashboard/organizations/${organization_id}/members`,
  organization_projects: (organization_id: string) => `/dashboard/organizations/${organization_id}/projects`,
  organization_billing: (organization_id: string) => `/dashboard/organizations/${organization_id}/billing`,
  organization_delete_verify: (organization_id: string) =>
    `/dashboard/organizations/${organization_id}/delete/verify`,
}

export const BILLING_PENDING_ORG_STORAGE_KEY = 'pending-billing-org-id'
