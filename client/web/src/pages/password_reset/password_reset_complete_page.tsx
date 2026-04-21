import { useState } from 'react'
import { Eye, EyeOff, Shield } from 'lucide-react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { handle_password_reset_complete } from '@/controllers/auth_controller'
import { ROUTES } from '@/lib/constants'
import type { PasswordResetCompleteState } from '@/types/auth_types'

export function PasswordResetCompletePage() {
  const navigate = useNavigate()
  const location = useLocation()
  const state = location.state as PasswordResetCompleteState | null

  const [new_password, set_new_password] = useState('')
  const [confirm_password, set_confirm_password] = useState('')
  const [show_password, set_show_password] = useState(false)
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)

  if (!state?.reset_token) {
    return <Navigate to={ROUTES.PASSWORD_RESET} replace />
  }

  const handle_submit = async (e: React.FormEvent) => {
    e.preventDefault()
    set_error(null)

    if (new_password !== confirm_password) {
      set_error('Passwords do not match.')
      return
    }

    set_loading(true)
    try {
      await handle_password_reset_complete(state.reset_token, new_password)
      navigate(ROUTES.LOGIN, { replace: true, state: { reset_success: true } })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      set_loading(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col items-center gap-2 text-center">
        <div className="flex h-10 w-10 items-center justify-center rounded-md border bg-background mb-2">
          <Shield className="h-6 w-6 text-foreground" strokeWidth={1.5} />
        </div>
        <h1 className="text-xl font-medium tracking-tight text-foreground">Set new password</h1>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Choose a strong password for your account.
        </p>
      </div>

      <form onSubmit={handle_submit} noValidate className="flex flex-col gap-4">
        <div className="grid gap-2">
          <Label htmlFor="new_password" title="New Password"  className="text-xs font-medium uppercase tracking-wider text-muted-foreground/80">New password</Label>
          <div className="relative">
            <Input
              id="new_password"
              type={show_password ? 'text' : 'password'}
              placeholder="••••••••"
              value={new_password}
              onChange={(e) => set_new_password(e.target.value)}
              required
              autoComplete="new-password"
              autoFocus
              className="h-10 pr-10 bg-background text-foreground"
            />
            <button
              type="button"
              onClick={() => set_show_password(!show_password)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              tabIndex={-1}
            >
              {show_password ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>
        <div className="grid gap-2">
          <Label htmlFor="confirm_password" title="Confirm Password"  className="text-xs font-medium uppercase tracking-wider text-muted-foreground/80">Confirm new password</Label>
          <Input
            id="confirm_password"
            type={show_password ? 'text' : 'password'}
            placeholder="••••••••"
            value={confirm_password}
            onChange={(e) => set_confirm_password(e.target.value)}
            required
            autoComplete="new-password"
            className="h-10 bg-background text-foreground"
          />
        </div>

        <Button type="submit" className="w-full h-10 font-medium bg-primary text-primary-foreground hover:bg-primary/90" disabled={loading}>
          {loading ? <LoadingSpinner size="sm" className="mr-2" /> : "Update password"}
        </Button>

        <ErrorAlert message={error} />
      </form>
    </div>
  )
}
