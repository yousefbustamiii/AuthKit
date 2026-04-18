import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { handle_password_reset_verify } from '@/controllers/auth_controller'
import { ROUTES } from '@/lib/constants'
import type { PasswordResetCompleteState, PasswordResetVerifyState } from '@/types/auth_types'

export function PasswordResetVerifyPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const state = location.state as PasswordResetVerifyState | null

  const [otp, set_otp] = useState('')
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)

  if (!state?.email) {
    return <Navigate to={ROUTES.PASSWORD_RESET} replace />
  }

  const { email } = state

  const submit_otp = async (value: string) => {
    if (value.length !== 6) return
    set_error(null)
    set_loading(true)
    try {
      const result = await handle_password_reset_verify(email, value)
      const next_state: PasswordResetCompleteState = { reset_token: result.reset_token }
      navigate(ROUTES.PASSWORD_RESET_COMPLETE, { state: next_state })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Invalid code. Please try again.')
      set_otp('')
    } finally {
      set_loading(false)
    }
  }

  const handle_otp_change = (value: string) => {
    set_otp(value)
    if (value.length === 6) {
      submit_otp(value)
    }
  }

  return (
    <Card className="shadow-sm">
      <CardHeader className="space-y-1 pb-4 text-center">
        <CardTitle className="text-2xl font-semibold">Enter reset code</CardTitle>
        <CardDescription>
          We sent a 6-digit code to <span className="font-medium text-foreground">{email}</span>
        </CardDescription>
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
          Verify code
        </Button>
      </CardContent>
    </Card>
  )
}
