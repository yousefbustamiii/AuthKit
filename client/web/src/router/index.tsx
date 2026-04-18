import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { PublicGuard } from './public_guard'
import { PrivateGuard } from './private_guard'
import { AuthLayout } from '@/layouts/auth_layout'
import { DashboardLayout } from '@/layouts/dashboard_layout'
import { OrganizationLayout } from '@/layouts/organization_layout'
import { PageLoader } from '@/components/shared/page_loader'
import { LoginPage } from '@/pages/login/login_page'
import { SignupPage } from '@/pages/signup/signup_page'
import { OtpPage } from '@/pages/otp/otp_page'
import { PasswordResetInitiatePage } from '@/pages/password_reset/password_reset_initiate_page'
import { PasswordResetVerifyPage } from '@/pages/password_reset/password_reset_verify_page'
import { PasswordResetCompletePage } from '@/pages/password_reset/password_reset_complete_page'
import { GoogleCallbackPage } from '@/pages/oauth/google_callback_page'
import { GitHubCallbackPage } from '@/pages/oauth/github_callback_page'
import { ROUTES } from '@/lib/constants'

const SessionsPage = lazy(() => import('@/pages/dashboard/sessions/sessions_page').then(m => ({ default: m.SessionsPage })))
const ProfilePage = lazy(() => import('@/pages/dashboard/profile/profile_page').then(m => ({ default: m.ProfilePage })))
const DevicesPage = lazy(() => import('@/pages/dashboard/devices/devices_page').then(m => ({ default: m.DevicesPage })))
const EmailChangePage = lazy(() => import('@/pages/dashboard/settings/email/email_change_page').then(m => ({ default: m.EmailChangePage })))
const PasswordChangePage = lazy(() => import('@/pages/dashboard/settings/password/password_change_page').then(m => ({ default: m.PasswordChangePage })))
const DeleteAccountPage = lazy(() => import('@/pages/dashboard/settings/delete/delete_account_page').then(m => ({ default: m.DeleteAccountPage })))
const OrganizationsPage = lazy(() => import('@/pages/dashboard/organizations/organizations_page').then(m => ({ default: m.OrganizationsPage })))
const OrganizationMembersPage = lazy(() => import('@/pages/dashboard/organizations/organization_members_page').then(m => ({ default: m.OrganizationMembersPage })))
const OrganizationProjectsPage = lazy(() => import('@/pages/dashboard/organizations/organization_projects_page').then(m => ({ default: m.OrganizationProjectsPage })))
const OrganizationBillingPage = lazy(() => import('@/pages/dashboard/organizations/organization_billing_page').then(m => ({ default: m.OrganizationBillingPage })))
const OrganizationDeleteVerifyPage = lazy(() => import('@/pages/dashboard/organizations/organization_delete_verify_page').then(m => ({ default: m.OrganizationDeleteVerifyPage })))
const AcceptInvitationPage = lazy(() => import('@/pages/dashboard/invitations/accept_invitation_page').then(m => ({ default: m.AcceptInvitationPage })))
const BillingSuccessPage = lazy(() => import('@/pages/billing/billing_success_page').then(m => ({ default: m.BillingSuccessPage })))
const BillingCancelPage = lazy(() => import('@/pages/billing/billing_cancel_page').then(m => ({ default: m.BillingCancelPage })))

export const router = createBrowserRouter([
  {
    path: ROUTES.ROOT,
    element: <Navigate to={ROUTES.LOGIN} replace />,
  },
  {
    element: <AuthLayout />,
    children: [
      { path: ROUTES.OTP, element: <OtpPage /> },
    ],
  },
  {
    element: <PublicGuard />,
    children: [
      {
        element: <AuthLayout />,
        children: [
          { path: ROUTES.LOGIN, element: <LoginPage /> },
          { path: ROUTES.SIGNUP, element: <SignupPage /> },
          { path: ROUTES.PASSWORD_RESET, element: <PasswordResetInitiatePage /> },
          { path: ROUTES.PASSWORD_RESET_VERIFY, element: <PasswordResetVerifyPage /> },
          { path: ROUTES.PASSWORD_RESET_COMPLETE, element: <PasswordResetCompletePage /> },
        ],
      },
      { path: ROUTES.OAUTH_GOOGLE_CALLBACK, element: <GoogleCallbackPage /> },
      { path: ROUTES.OAUTH_GITHUB_CALLBACK, element: <GitHubCallbackPage /> },
    ],
  },
  {
    element: <PrivateGuard />,
    children: [
      {
        path: ROUTES.DASHBOARD,
        element: <Suspense fallback={<PageLoader />}><DashboardLayout /></Suspense>,
        children: [
          { index: true, element: <SessionsPage /> },
          { path: 'organizations', element: <OrganizationsPage /> },
          { path: 'invitations/accept', element: <AcceptInvitationPage /> },
          {
            path: 'organizations/:organizationId',
            element: <OrganizationLayout />,
            children: [
              { index: true, element: <Navigate to="members" replace /> },
              { path: 'members', element: <OrganizationMembersPage /> },
              { path: 'projects', element: <OrganizationProjectsPage /> },
              { path: 'billing', element: <OrganizationBillingPage /> },
              { path: 'delete/verify', element: <OrganizationDeleteVerifyPage /> },
            ],
          },
          { path: 'profile', element: <ProfilePage /> },
          { path: 'devices', element: <DevicesPage /> },
          { path: 'settings/email', element: <EmailChangePage /> },
          { path: 'settings/password', element: <PasswordChangePage /> },
          { path: 'settings/delete', element: <DeleteAccountPage /> },
        ],
      },
    ],
  },
  { path: ROUTES.BILLING_SUCCESS, element: <BillingSuccessPage /> },
  { path: ROUTES.BILLING_CANCEL, element: <BillingCancelPage /> },
])
