import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { ExternalLink } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
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
    <div className="space-y-6 max-w-5xl">
      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-card/40 border-border/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold tracking-tight uppercase text-muted-foreground/80">Plan Details</CardTitle>
          </CardHeader>
          <CardContent>
            {!billing?.subscription ? (
              <p className="text-xs text-muted-foreground">No active subscription yet.</p>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-bold tracking-tight capitalize leading-none mb-1">{billing.subscription.plan.replace('_', ' ')}</h3>
                    <div className="flex items-center gap-2">
                      <Badge className="h-5 px-1.5 text-[10px] uppercase font-bold tracking-wider">{billing.subscription.status}</Badge>
                      {billing.subscription.cancel_at_period_end && <Badge variant="outline" className="h-5 px-1.5 text-[10px] uppercase font-bold">Planned Cancel</Badge>}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-[11px] font-bold uppercase text-muted-foreground/60 tracking-wider">Next Renewal</p>
                    <p className="text-sm font-semibold">{new Date(billing.subscription.current_period_end).toLocaleDateString()}</p>
                  </div>
                </div>

                {is_owner && !billing.subscription.cancel_at_period_end && (
                  <Button variant="outline" size="sm" className="w-full text-xs h-8 border-destructive/20 text-destructive hover:bg-destructive hover:text-destructive-foreground transition-all" onClick={handle_cancel} disabled={cancel_loading}>
                    {cancel_loading ? <LoadingSpinner size="sm" /> : "Cancel Subscription"}
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="bg-card/40 border-border/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold tracking-tight uppercase text-muted-foreground/80">Available Tiers</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {PLAN_OPTIONS.map((plan) => {
              const is_current = current_plan_number === plan.number
              const can_upgrade = is_owner && billing?.subscription && current_plan_number !== null && subscription_status !== 'canceled' && subscription_status !== 'incomplete_expired' && plan.number > current_plan_number
              const can_checkout = is_owner && can_checkout_again

              return (
                <div key={plan.number} className="flex items-center justify-between p-2 rounded-md border border-transparent hover:border-border/50 hover:bg-accent/10 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-2 rounded-full bg-primary/20" />
                    <div>
                      <p className="text-[13px] font-semibold">{plan.label}</p>
                      {is_current && <p className="text-[11px] text-primary/80 font-bold uppercase tracking-wider">Current Plan</p>}
                    </div>
                  </div>
                  <div>
                    {can_checkout && (
                      <Button size="sm" className="h-7 text-[11px] px-3 font-bold" onClick={() => handle_checkout(plan.number)} disabled={busy_plan === plan.number}>
                        {busy_plan === plan.number ? <LoadingSpinner size="sm" /> : "Upgrade"}
                      </Button>
                    )}
                    {can_upgrade && (
                      <Button size="sm" className="h-7 text-[11px] px-3 font-bold" variant="outline" onClick={() => handle_upgrade(plan.number)} disabled={busy_plan === plan.number}>
                        Upgrade
                      </Button>
                    )}
                    {!can_checkout && !can_upgrade && is_current && (
                      <Badge variant="secondary" className="h-6 text-[10px] font-bold">Active</Badge>
                    )}
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>
      </div>

      <Card className="bg-card/20 border-border/50">
        <CardHeader className="pb-3 border-b border-border/50">
          <CardTitle className="text-sm font-semibold tracking-tight uppercase text-muted-foreground/80">Billing History</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="w-full overflow-hidden">
            {billing?.invoices.length ? (
              <div className="divide-y divide-border/50">
                {billing.invoices.map((invoice) => (
                  <div key={invoice.invoice_id} className="grid grid-cols-4 items-center gap-4 px-6 py-3 hover:bg-accent/5 transition-all text-xs">
                    <div className="font-semibold text-foreground">
                      {new Date(invoice.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </div>
                    <div className="flex items-center gap-2">
                       <span className="font-bold text-[13px]">{invoice.currency.toUpperCase()} {(invoice.amount / 100).toFixed(2)}</span>
                       <Badge variant="outline" className="text-[10px] px-1.5 h-5 capitalize bg-background">{invoice.status}</Badge>
                    </div>
                    <div className="text-muted-foreground/60 font-mono scale-90">
                      #{invoice.invoice_id.slice(-8).toUpperCase()}
                    </div>
                    <div className="text-right">
                      {invoice.hosted_invoice_url ? (
                        <a href={invoice.hosted_invoice_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 text-primary hover:underline font-bold tracking-tight">
                          View Invoice <ExternalLink className="h-3 w-3" />
                        </a>
                      ) : (
                        <span className="text-muted-foreground/40 italic">N/A</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center">
                <p className="text-xs text-muted-foreground">No transaction history available yet.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      <ErrorAlert message={error} />
    </div>
  )
}
