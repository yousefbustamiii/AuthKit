import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { ErrorAlert } from '@/components/shared/error_alert'
import { GoogleOAuthButton, GitHubOAuthButton } from '@/components/shared/oauth_buttons'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { handle_signup_initiate } from '@/controllers/auth_controller'
import { ROUTES } from '@/lib/constants'
import type { OtpRouterState } from '@/types/auth_types'

export function SignupPage() {
  const navigate = useNavigate()
  const [email, set_email] = useState('')
  const [password, set_password] = useState('')
  const [confirm_password, set_confirm_password] = useState('')
  const [show_password, set_show_password] = useState(false)
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)

  const handle_submit = async (e: React.FormEvent) => {
    e.preventDefault()
    set_error(null)

    if (password !== confirm_password) {
      set_error('Passwords do not match.')
      return
    }

    set_loading(true)
    try {
      const result = await handle_signup_initiate(email, password)
      const state: OtpRouterState = { context: 'signup', email_hash: result.email_hash, email }
      navigate(ROUTES.OTP, { state })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      set_loading(false)
    }
  }

  return (
    <Card className="shadow-sm">
      <CardHeader className="space-y-1 pb-4">
        <CardTitle className="text-2xl font-semibold">Create an account</CardTitle>
        <CardDescription>Start your journey — it&apos;s free</CardDescription>
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
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <div className="relative">
              <Input
                id="password"
                type={show_password ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => set_password(e.target.value)}
                required
                autoComplete="new-password"
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
            <Label htmlFor="confirm_password">Confirm password</Label>
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
            Create account
          </Button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <Separator />
          </div>
          <div className="relative flex justify-center text-xs">
            <span className="bg-card px-2 text-muted-foreground">or continue with</span>
          </div>
        </div>

        <div className="space-y-2">
          <GoogleOAuthButton />
          <GitHubOAuthButton />
        </div>
      </CardContent>
      <CardFooter className="justify-center border-t pt-4">
        <p className="text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link to={ROUTES.LOGIN} className="font-medium text-foreground underline-offset-4 hover:underline">
            Sign in
          </Link>
        </p>
      </CardFooter>
    </Card>
  )
}
