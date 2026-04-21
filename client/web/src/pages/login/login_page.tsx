import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorAlert } from '@/components/shared/error_alert'
import { GoogleOAuthButton, GitHubOAuthButton } from '@/components/shared/oauth_buttons'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { handle_login_initiate } from '@/controllers/auth_controller'
import { ROUTES } from '@/lib/constants'
import type { OtpRouterState } from '@/types/auth_types'

export function LoginPage() {
  const navigate = useNavigate()
  const [email, set_email] = useState('')
  const [password, set_password] = useState('')
  const [show_password, set_show_password] = useState(false)
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)

  const handle_submit = async (e: React.FormEvent) => {
    e.preventDefault()
    set_error(null)
    set_loading(true)
    try {
      const result = await handle_login_initiate(email, password)
      if (result.needs_otp) {
        const state: OtpRouterState = { context: 'login', email_hash: result.email_hash, email }
        navigate(ROUTES.OTP, { state })
      } else {
        navigate(ROUTES.DASHBOARD, { replace: true })
      }
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
        <h1 className="text-xl font-medium tracking-tight text-foreground">Welcome to AuthKit</h1>
        <p className="text-sm text-muted-foreground">
          Don&apos;t have an account?{' '}
          <Link to={ROUTES.SIGNUP} className="underline underline-offset-4 font-medium hover:text-foreground transition-colors">
            Sign up
          </Link>
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
        <div className="grid gap-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="password" className="text-xs font-medium uppercase tracking-wider text-muted-foreground/80">Password</Label>
          </div>
          <div className="relative">
            <Input
              id="password"
              type={show_password ? 'text' : 'password'}
              placeholder="••••••••"
              value={password}
              onChange={(e) => set_password(e.target.value)}
              required
              autoComplete="current-password"
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
          <div className="flex justify-end">
             <Link
                to={ROUTES.PASSWORD_RESET}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                Forgot your password?
              </Link>
          </div>
        </div>

        <ErrorAlert message={error} />

        <Button type="submit" className="w-full h-10 font-medium bg-primary text-primary-foreground hover:bg-primary/90" disabled={loading}>
          {loading ? <LoadingSpinner size="sm" className="mr-2" /> : "Login"}
        </Button>
      </form>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground font-medium tracking-widest">Or</span>
        </div>
      </div>

      <div className="grid gap-2">
        <GitHubOAuthButton />
        <GoogleOAuthButton />
      </div>

      <p className="px-8 text-center text-[11px] leading-relaxed text-muted-foreground/60">
        By clicking continue, you agree to our{' '}
        <a href="#" className="underline underline-offset-4 hover:text-foreground">
          Terms of Service
        </a>{' '}
        and{' '}
        <a href="#" className="underline underline-offset-4 hover:text-foreground">
          Privacy Policy
        </a>
        .
      </p>
    </div>
  )
}
