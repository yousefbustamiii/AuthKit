import { useEffect, useRef, useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from '@/components/ui/input-otp'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import {
  handle_signup_complete,
  handle_login_complete,
  handle_resend_otp_public,
  handle_resend_otp_authenticated,
} from '@/controllers/auth_controller'
import {
  handle_email_change_complete,
  handle_account_delete_complete,
} from '@/controllers/dashboard_controller'
import { ROUTES } from '@/lib/constants'
import type { OtpContext, OtpRouterState } from '@/types/auth_types'

const RESEND_COOLDOWN = 30

interface OtpConfig {
  title: string
  description: (email?: string) => string
}

const otp_config: Record<OtpContext, OtpConfig> = {
  signup: {
    title: 'Verify your email',
    description: (email) =>
      email
        ? `Enter the 6-digit code sent to ${email}.`
        : 'Enter the 6-digit code sent to your email address.',
  },
  login: {
    title: 'Two-factor verification',
    description: (email) =>
      email
        ? `Enter the 6-digit code sent to ${email}.`
        : 'Enter the 6-digit code sent to your email address.',
  },
  email_change: {
    title: 'Confirm email change',
    description: () => 'Enter the 6-digit code sent to your new email address.',
  },
  account_delete: {
    title: 'Confirm account deletion',
    description: () => 'Enter the 6-digit code to permanently delete your account.',
  },
}

function is_valid_state(state: OtpRouterState): boolean {
  if (!state.context) return false
  if (state.context === 'signup' || state.context === 'login') {
    return Boolean(state.email_hash && state.email)
  }
  return true
}

export function OtpPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const state = location.state as OtpRouterState | null

  const [otp, set_otp] = useState('')
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)
  const [resend_error, set_resend_error] = useState<string | null>(null)
  const [cooldown, set_cooldown] = useState(0)

  const cooldown_ref = useRef<ReturnType<typeof setInterval> | null>(null)
  const is_submitting = useRef(false)

  useEffect(() => {
    return () => {
      if (cooldown_ref.current) clearInterval(cooldown_ref.current)
    }
  }, [])

  if (!state || !is_valid_state(state)) {
    return <Navigate to={ROUTES.LOGIN} replace />
  }

  const { context, email_hash, email } = state
  const config = otp_config[context]

  const submit_otp = async (value: string) => {
    if (value.length !== 6 || is_submitting.current) return
    is_submitting.current = true
    set_error(null)
    set_loading(true)

    try {
      if (context === 'signup') {
        await handle_signup_complete(email_hash!, value)
        navigate(ROUTES.DASHBOARD, { replace: true })
      } else if (context === 'login') {
        await handle_login_complete(email_hash!, value)
        navigate(ROUTES.DASHBOARD, { replace: true })
      } else if (context === 'email_change') {
        await handle_email_change_complete(value)
        navigate(ROUTES.DASHBOARD_SETTINGS_EMAIL, { replace: true, state: { success: true } })
      } else if (context === 'account_delete') {
        // controller already clears auth store on success
        await handle_account_delete_complete(value)
        navigate(ROUTES.LOGIN, { replace: true, state: { deleted: true } })
      }
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Invalid code. Please try again.')
      set_otp('')
    } finally {
      set_loading(false)
      is_submitting.current = false
    }
  }

  const handle_otp_change = (value: string) => {
    set_otp(value)
    if (value.length === 6) {
      submit_otp(value)
    }
  }

  const handle_resend = async () => {
    if (cooldown > 0) return
    set_resend_error(null)

    try {
      if (context === 'signup' || context === 'login') {
        await handle_resend_otp_public(email!, email_hash!)
      } else {
        await handle_resend_otp_authenticated()
      }

      set_cooldown(RESEND_COOLDOWN)
      cooldown_ref.current = setInterval(() => {
        set_cooldown((prev) => {
          if (prev <= 1) {
            clearInterval(cooldown_ref.current!)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    } catch (err) {
      set_resend_error(err instanceof Error ? err.message : 'Failed to resend code. Please try again.')
    }
  }

  return (
    <Card className="shadow-sm">
      <CardHeader className="space-y-1 pb-4 text-center">
        <CardTitle className="text-2xl font-semibold">{config.title}</CardTitle>
        <CardDescription>{config.description(email)}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex justify-center">
          <InputOTP
            maxLength={6}
            value={otp}
            onChange={handle_otp_change}
            disabled={loading}
          >
            <InputOTPGroup>
              <InputOTPSlot index={0} />
              <InputOTPSlot index={1} />
              <InputOTPSlot index={2} />
              <InputOTPSlot index={3} />
              <InputOTPSlot index={4} />
              <InputOTPSlot index={5} />
            </InputOTPGroup>
          </InputOTP>
        </div>

        <ErrorAlert message={error} />

        <Button
          className="w-full"
          onClick={() => submit_otp(otp)}
          disabled={loading || otp.length < 6}
        >
          {loading && <LoadingSpinner size="sm" className="mr-2 text-primary-foreground" />}
          Verify
        </Button>

        <div className="space-y-1.5 text-center text-sm text-muted-foreground">
          <div>
            Didn&apos;t receive a code?{' '}
            <button
              type="button"
              onClick={handle_resend}
              disabled={cooldown > 0}
              className="font-medium text-foreground underline-offset-4 hover:underline disabled:cursor-not-allowed disabled:opacity-50"
            >
              {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend'}
            </button>
          </div>
          {resend_error && (
            <p className="text-xs text-destructive">{resend_error}</p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
