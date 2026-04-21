import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Shield } from 'lucide-react'
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
    <div className="flex flex-col gap-6">
      <div className="flex flex-col items-center gap-2 text-center">
        <div className="flex h-10 w-10 items-center justify-center rounded-md border bg-background mb-2">
          <Shield className="h-6 w-6 text-foreground" strokeWidth={1.5} />
        </div>
        <h1 className="text-xl font-medium tracking-tight text-foreground">Reset your password</h1>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Enter your email and we&apos;ll send you a verification code.
        </p>
      </div>

      <form onSubmit={handle_submit} className="flex flex-col gap-4">
        <div className="grid gap-2">
          <Label htmlFor="email" className="text-xs font-medium uppercase tracking-wider text-muted-foreground/80">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="m@example.com"
            value={email}
            onChange={(e) => set_email(e.target.value)}
            required
            autoComplete="email"
            className="h-10 bg-background text-foreground"
            autoFocus
          />
        </div>

        <ErrorAlert message={error} />

        <Button type="submit" className="w-full h-10 font-medium bg-primary text-primary-foreground hover:bg-primary/90" disabled={loading}>
          {loading ? <LoadingSpinner size="sm" className="mr-2" /> : "Send reset code"}
        </Button>
      </form>

      <Link
        to={ROUTES.LOGIN}
        className="flex items-center justify-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to sign in
      </Link>
    </div>
  )
}
