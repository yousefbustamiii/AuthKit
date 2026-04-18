import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { handle_password_reset_initiate } from '@/controllers/auth_controller'
import { ROUTES } from '@/lib/constants'
import type { PasswordResetVerifyState } from '@/types/auth_types'

export function PasswordResetInitiatePage() {
  const navigate = useNavigate()
  const [email, set_email] = useState('')
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)

  const handle_submit = async (e: React.FormEvent) => {
    e.preventDefault()
    set_error(null)
    set_loading(true)
    try {
      await handle_password_reset_initiate(email)
      const state: PasswordResetVerifyState = { email }
      navigate(ROUTES.PASSWORD_RESET_VERIFY, { state })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      set_loading(false)
    }
  }

  return (
    <Card className="shadow-sm">
      <CardHeader className="space-y-1 pb-4">
        <CardTitle className="text-2xl font-semibold">Reset your password</CardTitle>
        <CardDescription>
          Enter your email and we&apos;ll send you a verification code.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handle_submit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => set_email(e.target.value)}
              required
              autoComplete="email"
              autoFocus
            />
          </div>

          <ErrorAlert message={error} />

          <Button type="submit" className="w-full" disabled={loading}>
            {loading && <LoadingSpinner size="sm" className="mr-2 text-primary-foreground" />}
            Send reset code
          </Button>
        </form>

        <Link
          to={ROUTES.LOGIN}
          className="flex items-center justify-center gap-1.5 text-sm text-muted-foreground underline-offset-4 hover:underline"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to sign in
        </Link>
      </CardContent>
    </Card>
  )
}
