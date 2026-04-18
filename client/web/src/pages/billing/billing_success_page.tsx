import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle2 } from 'lucide-react'
import { BILLING_PENDING_ORG_STORAGE_KEY, core_routes, ROUTES } from '@/lib/constants'

export function BillingSuccessPage() {
  const navigate = useNavigate()

  useEffect(() => {
    const organization_id = sessionStorage.getItem(BILLING_PENDING_ORG_STORAGE_KEY)
    sessionStorage.removeItem(BILLING_PENDING_ORG_STORAGE_KEY)
    const target = organization_id ? core_routes.organization_billing(organization_id) : ROUTES.DASHBOARD_ORGANIZATIONS
    navigate(target, { replace: true, state: { checkout_status: 'success' } })
  }, [navigate])

  return (
    <div className="flex h-screen items-center justify-center">
      <div className="flex items-center gap-3 text-sm text-muted-foreground">
        <CheckCircle2 className="h-5 w-5 text-green-600" />
        Redirecting to billing…
      </div>
    </div>
  )
}
