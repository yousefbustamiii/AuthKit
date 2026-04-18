import { Navigate, Outlet } from 'react-router-dom'
import { use_auth_store } from '@/store/auth_store'
import { PageLoader } from '@/components/shared/page_loader'
import { ROUTES } from '@/lib/constants'
import { useSessionCheck } from '@/router/use_session_check'

export function PublicGuard() {
  const { is_authenticated, is_loading } = use_auth_store()
  useSessionCheck()

  if (is_loading) return <PageLoader />
  if (is_authenticated) return <Navigate to={ROUTES.DASHBOARD} replace />
  return <Outlet />
}
