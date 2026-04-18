import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { ExternalLink } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { cancel_billing, load_organization_billing, start_checkout, upgrade_billing } from '@/controllers/core_controller'
import { use_core_store } from '@/store/core_store'
import { toast } from '@/hooks/use-toast'
import { BILLING_PENDING_ORG_STORAGE_KEY, core_routes } from '@/lib/constants'

const PLAN_OPTIONS = [
  { number: 1, label: 'Plan 1' },
  { number: 2, label: 'Plan 2' },
  { number: 3, label: 'Plan 3' },
]

export function OrganizationBillingPage() {
  const { organizationId = '' } = useParams<{ organizationId: string }>()
  const location = useLocation()
  const navigate = useNavigate()
  const organizations = use_core_store((s) => s.organizations)
  const billing = use_core_store((s) => s.billing_by_org[organizationId] ?? null)
  const organization = organizations.find((item) => item.organization_id === organizationId)
  const is_owner = organization?.current_user_role === 'owner'

  const [loading, set_loading] = useState(true)
  const [error, set_error] = useState<string | null>(null)
  const [busy_plan, set_busy_plan] = useState<number | null>(null)
  const [cancel_loading, set_cancel_loading] = useState(false)

  const subscription_status = billing?.subscription?.status ?? null
  const can_checkout_again =
    billing?.subscription == null ||
    subscription_status === 'canceled' ||
    subscription_status === 'incomplete_expired'

  useEffect(() => {
    load_organization_billing(organizationId)
      .catch(() => undefined)
      .finally(() => set_loading(false))
  }, [organizationId])

  useEffect(() => {
    const state = location.state as { checkout_status?: 'success' | 'canceled' } | null
    if (state?.checkout_status === 'success') {
      toast({ title: 'Checkout complete', description: 'Billing details are refreshing from Stripe webhook data.' })
    }
    if (state?.checkout_status === 'canceled') {
      toast({ title: 'Checkout canceled', description: 'No subscription changes were applied.' })
    }
    if (state?.checkout_status) {
      navigate(core_routes.organization_billing(organizationId), { replace: true })
    }
  }, [location.state, navigate, organizationId])

  useEffect(() => {
    const state = location.state as { checkout_status?: 'success' | 'canceled' } | null
    if (state?.checkout_status !== 'success') return

    let cancelled = false
    let attempts = 0

    const poll = async () => {
      while (!cancelled && attempts < 8) {
        attempts += 1
        const next_billing = await load_organization_billing(organizationId)
        const next_status = next_billing.subscription?.status ?? null
        if (
          next_billing.subscription !== null &&
          next_status !== 'canceled' &&
          next_status !== 'incomplete_expired'
        ) {
          return
        }
        await new Promise((resolve) => window.setTimeout(resolve, 1500))
      }
    }

    poll().catch(() => undefined)

    return () => {
      cancelled = true
    }
  }, [location.state, organizationId])

  const current_plan_number = useMemo(() => {
    if (!billing?.subscription?.plan?.startsWith('plan_')) return null
    return Number.parseInt(billing.subscription.plan.split('_')[1] ?? '', 10)
  }, [billing?.subscription?.plan])

  const handle_checkout = async (plan_number: number) => {
    set_error(null)
    set_busy_plan(plan_number)
    try {
      sessionStorage.setItem(BILLING_PENDING_ORG_STORAGE_KEY, organizationId)
      const checkout_url = await start_checkout(organizationId, plan_number)
      window.location.href = checkout_url
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
      sessionStorage.removeItem(BILLING_PENDING_ORG_STORAGE_KEY)
      setBusy(null)
    }
  }

  const setBusy = (value: number | null) => set_busy_plan(value)

  const handle_upgrade = async (plan_number: number) => {
    set_error(null)
    setBusy(plan_number)
    try {
      await upgrade_billing(organizationId, plan_number)
      toast({ title: 'Plan updated', description: `Upgrade to plan ${plan_number} requested successfully.` })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setBusy(null)
    }
  }

  const handle_cancel = async () => {
    set_error(null)
    set_cancel_loading(true)
    try {
      await cancel_billing(organizationId)
      toast({ title: 'Cancellation scheduled', description: 'The subscription will end at the current billing period.' })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      set_cancel_loading(false)
    }
  }

  if (loading) {
    return <div className="flex h-64 items-center justify-center"><LoadingSpinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Current subscription</CardTitle>
          <CardDescription>Stripe-backed billing state for this organization.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!billing?.subscription ? (
            <p className="text-sm text-muted-foreground">No active subscription yet.</p>
          ) : (
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">Plan</p>
                <p className="mt-2 text-lg font-semibold capitalize">{billing.subscription.plan.replace('_', ' ')}</p>
              </div>
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">Status</p>
                <div className="mt-2 flex items-center gap-2">
                  <Badge className="capitalize">{billing.subscription.status}</Badge>
                  {billing.subscription.cancel_at_period_end && <Badge variant="outline">Canceling at period end</Badge>}
                </div>
              </div>
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">Current period end</p>
                <p className="mt-2 text-lg font-semibold">{new Date(billing.subscription.current_period_end).toLocaleDateString()}</p>
              </div>
            </div>
          )}

          {is_owner && billing?.subscription && !billing.subscription.cancel_at_period_end && (
            <Button variant="destructive" onClick={handle_cancel} disabled={cancel_loading}>
              Cancel subscription
            </Button>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Plans</CardTitle>
          <CardDescription>Start checkout for a new subscription or upgrade your current plan.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          {PLAN_OPTIONS.map((plan) => {
            const is_current = current_plan_number === plan.number
            const can_upgrade =
              is_owner &&
              billing?.subscription &&
              current_plan_number !== null &&
              subscription_status !== 'canceled' &&
              subscription_status !== 'incomplete_expired' &&
              plan.number > current_plan_number
            const can_checkout = is_owner && can_checkout_again

            return (
              <div key={plan.number} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <p className="font-medium">{plan.label}</p>
                  {is_current && <Badge variant="secondary">Current</Badge>}
                </div>
                <p className="mt-2 text-sm text-muted-foreground">Use Stripe checkout and webhook sync for final billing state.</p>
                <div className="mt-4">
                  {can_checkout && (
                    <Button onClick={() => handle_checkout(plan.number)} disabled={busy_plan === plan.number}>
                      {busy_plan === plan.number && <LoadingSpinner size="sm" className="text-primary-foreground" />}
                      Checkout
                    </Button>
                  )}
                  {can_upgrade && (
                    <Button onClick={() => handle_upgrade(plan.number)} disabled={busy_plan === plan.number}>
                      Upgrade
                    </Button>
                  )}
                  {!can_checkout && !can_upgrade && (
                    <Button variant="outline" disabled>
                      {is_current ? 'Current plan' : 'Unavailable'}
                    </Button>
                  )}
                </div>
              </div>
            )
          })}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium">Invoices</CardTitle>
          <CardDescription>{billing?.invoices.length ?? 0} invoices synced from Stripe webhooks.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {billing?.invoices.length ? (
            billing.invoices.map((invoice) => (
              <div key={invoice.invoice_id} className="flex flex-wrap items-center justify-between gap-4 rounded-lg border p-4">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium">{invoice.currency.toUpperCase()} {(invoice.amount / 100).toFixed(2)}</p>
                    <Badge variant="outline" className="capitalize">{invoice.status}</Badge>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">{new Date(invoice.created_at).toLocaleString()}</p>
                </div>
                {invoice.hosted_invoice_url ? (
                  <Button variant="outline" asChild>
                    <a href={invoice.hosted_invoice_url} target="_blank" rel="noreferrer">
                      <ExternalLink className="h-4 w-4" />
                      Open invoice
                    </a>
                  </Button>
                ) : (
                  <Badge variant="secondary">No hosted URL</Badge>
                )}
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No invoices yet.</p>
          )}
        </CardContent>
      </Card>

      <ErrorAlert message={error} />
    </div>
  )
}
