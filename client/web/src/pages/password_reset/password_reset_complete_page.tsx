import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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
    <Card className="shadow-sm">
      <CardHeader className="space-y-1 pb-4">
        <CardTitle className="text-2xl font-semibold">Set new password</CardTitle>
        <CardDescription>Choose a strong password for your account.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handle_submit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="new_password">New password</Label>
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
                className="pr-10"
              />
              <button
                type="button"
                onClick={() => set_show_password(!show_password)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                tabIndex={-1}
              >
                {show_password ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm_password">Confirm new password</Label>
            <Input
              id="confirm_password"
              type={show_password ? 'text' : 'password'}
              placeholder="••••••••"
              value={confirm_password}
              onChange={(e) => set_confirm_password(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          <ErrorAlert message={error} />

          <Button type="submit" className="w-full" disabled={loading}>
            {loading && <LoadingSpinner size="sm" className="mr-2 text-primary-foreground" />}
            Update password
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
