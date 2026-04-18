import { useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { PageLoader } from '@/components/shared/page_loader'
import { handle_google_oauth_callback } from '@/controllers/auth_controller'
import { ROUTES } from '@/lib/constants'

export function GoogleCallbackPage() {
  const navigate = useNavigate()
  const [search_params] = useSearchParams()
  const called = useRef(false)

  useEffect(() => {
    if (called.current) return
    called.current = true

    const code = search_params.get('code')
    const state = search_params.get('state')

    if (!code || !state) {
      navigate(ROUTES.LOGIN, { replace: true })
      return
    }

    handle_google_oauth_callback(code, state)
      .then(() => navigate(ROUTES.DASHBOARD, { replace: true }))
      .catch(() => navigate(ROUTES.LOGIN, { replace: true }))
  }, [navigate, search_params])

  return <PageLoader />
}
