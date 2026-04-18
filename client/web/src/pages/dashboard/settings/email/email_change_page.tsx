import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { CheckCircle2, ShieldAlert } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { handle_email_change_initiate, load_profile } from '@/controllers/dashboard_controller'
import { use_auth_store } from '@/store/auth_store'
import { use_dashboard_store } from '@/store/dashboard_store'
import { ROUTES } from '@/lib/constants'
import type { OtpRouterState } from '@/types/auth_types'

export function EmailChangePage() {
  const navigate = useNavigate()
  const location = useLocation()
  const current_email = use_auth_store((s) => s.user?.email)
  const profile = use_dashboard_store((s) => s.profile)
  const success = (location.state as { success?: boolean } | null)?.success

  const [new_email, set_new_email] = useState('')
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)
  const [profile_loading, set_profile_loading] = useState(!profile)

  useEffect(() => {
    if (!profile) {
      load_profile().finally(() => set_profile_loading(false))
    }
  }, [profile])

  if (profile_loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (profile && profile.provider !== 'email') {
    return (
      <div className="p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight">Change Email</h1>
          <p className="mt-1 text-sm text-muted-foreground">Update your account email address.</p>
        </div>
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3">
              <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
              <div className="text-sm text-amber-800">
                <p className="font-medium">Not available for OAuth accounts</p>
                <p className="mt-0.5 text-amber-700">
                  Your account is linked to <span className="font-medium capitalize">{profile.provider}</span>. Email changes are not supported for OAuth accounts.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const handle_submit = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    set_error(null)
    set_loading(true)
    try {
      await handle_email_change_initiate(new_email)
      const state: OtpRouterState = { context: 'email_change' }
      navigate(ROUTES.OTP, { state })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      set_loading(false)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Change Email</h1>
        <p className="mt-1 text-sm text-muted-foreground">Update your account email address.</p>
      </div>

      <Card className="max-w-md">
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-medium">New email address</CardTitle>
          <CardDescription>
            A verification code will be sent to your new email address.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {success && (
            <div className="mb-4 flex items-center gap-2 rounded-md border border-green-200 bg-green-50 px-3 py-2.5 text-sm text-green-700">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              Your email address has been updated successfully.
            </div>
          )}

          <form onSubmit={handle_submit} className="space-y-4">
            <div className="space-y-2">
              <Label>Current email</Label>
              <Input value={current_email ?? ''} disabled className="bg-muted/50" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new_email">New email</Label>
              <Input
                id="new_email"
                type="email"
                placeholder="new@example.com"
                value={new_email}
                onChange={(e) => set_new_email(e.target.value)}
                required
                autoFocus
              />
            </div>

            <ErrorAlert message={error} />

            <Button type="submit" disabled={loading}>
              {loading && <LoadingSpinner size="sm" className="mr-2 text-primary-foreground" />}
              Send verification code
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
