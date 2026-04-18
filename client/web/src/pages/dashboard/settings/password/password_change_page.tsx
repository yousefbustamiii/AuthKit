import { useEffect, useState } from 'react'
import { Eye, EyeOff, CheckCircle2, ShieldAlert } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { handle_password_change, load_profile } from '@/controllers/dashboard_controller'
import { use_dashboard_store } from '@/store/dashboard_store'

export function PasswordChangePage() {
  const profile = use_dashboard_store((s) => s.profile)
  const [old_password, set_old_password] = useState('')
  const [new_password, set_new_password] = useState('')
  const [confirm_password, set_confirm_password] = useState('')
  const [show_passwords, set_show_passwords] = useState(false)
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)
  const [success, set_success] = useState(false)
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
          <h1 className="text-2xl font-semibold tracking-tight">Change Password</h1>
          <p className="mt-1 text-sm text-muted-foreground">Update your password. All other sessions will be signed out.</p>
        </div>
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3">
              <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
              <div className="text-sm text-amber-800">
                <p className="font-medium">Not available for OAuth accounts</p>
                <p className="mt-0.5 text-amber-700">
                  Your account is linked to <span className="font-medium capitalize">{profile.provider}</span>. Password management is handled by your OAuth provider.
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
    set_success(false)

    if (new_password !== confirm_password) {
      set_error('New passwords do not match.')
      return
    }

    set_loading(true)
    try {
      await handle_password_change(old_password, new_password)
      set_success(true)
      set_old_password('')
      set_new_password('')
      set_confirm_password('')
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      set_loading(false)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Change Password</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Update your password. All other sessions will be signed out.
        </p>
      </div>

      <Card className="max-w-md">
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-medium">Update password</CardTitle>
          <CardDescription>
            Choose a strong password you haven&apos;t used before.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handle_submit} className="space-y-4">
            {success && (
              <div className="flex items-center gap-2 rounded-md border border-green-200 bg-green-50 px-3 py-2.5 text-sm text-green-700">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                Password updated successfully. Other sessions have been signed out.
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="old_password">Current password</Label>
              <div className="relative">
                <Input
                  id="old_password"
                  type={show_passwords ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={old_password}
                  onChange={(e) => set_old_password(e.target.value)}
                  required
                  autoComplete="current-password"
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => set_show_passwords(!show_passwords)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  tabIndex={-1}
                >
                  {show_passwords ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="new_password">New password</Label>
              <Input
                id="new_password"
                type={show_passwords ? 'text' : 'password'}
                placeholder="••••••••"
                value={new_password}
                onChange={(e) => set_new_password(e.target.value)}
                required
                autoComplete="new-password"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm_password">Confirm new password</Label>
              <Input
                id="confirm_password"
                type={show_passwords ? 'text' : 'password'}
                placeholder="••••••••"
                value={confirm_password}
                onChange={(e) => set_confirm_password(e.target.value)}
                required
                autoComplete="new-password"
              />
            </div>

            <ErrorAlert message={error} />

            <Button type="submit" disabled={loading}>
              {loading && <LoadingSpinner size="sm" className="mr-2 text-primary-foreground" />}
              Update password
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
