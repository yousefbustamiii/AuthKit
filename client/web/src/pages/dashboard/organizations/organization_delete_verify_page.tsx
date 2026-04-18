import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { complete_organization_delete, resend_organization_delete_otp } from '@/controllers/core_controller'
import { ROUTES } from '@/lib/constants'

const RESEND_COOLDOWN = 30

export function OrganizationDeleteVerifyPage() {
  const navigate = useNavigate()
  const { organizationId = '' } = useParams<{ organizationId: string }>()

  const [otp, set_otp] = useState('')
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)
  const [resend_error, set_resend_error] = useState<string | null>(null)
  const [cooldown, set_cooldown] = useState(0)
  const cooldown_ref = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    return () => {
      if (cooldown_ref.current) clearInterval(cooldown_ref.current)
    }
  }, [])

  const submit = async (value: string) => {
    if (value.length !== 6) return
    set_error(null)
    set_loading(true)
    try {
      await complete_organization_delete(organizationId, value)
      navigate(ROUTES.DASHBOARD_ORGANIZATIONS, { replace: true })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Invalid code. Please try again.')
      set_otp('')
    } finally {
      set_loading(false)
    }
  }

  const resend = async () => {
    if (cooldown > 0) return
    set_resend_error(null)
    try {
      await resend_organization_delete_otp(organizationId)
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
    } catch {
      set_resend_error('Failed to resend code. Please try again.')
    }
  }

  return (
    <div className="max-w-md">
      <Card>
        <CardHeader className="space-y-1 pb-4">
          <CardTitle className="text-2xl font-semibold">Confirm organization deletion</CardTitle>
          <CardDescription>Enter the 6-digit code sent to your email to permanently delete this organization.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex justify-center">
            <InputOTP
              maxLength={6}
              value={otp}
              onChange={(value) => {
                set_otp(value)
                if (value.length === 6) submit(value)
              }}
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

          <Button className="w-full" onClick={() => submit(otp)} disabled={loading || otp.length < 6}>
            {loading && <LoadingSpinner size="sm" className="mr-2 text-primary-foreground" />}
            Verify and delete
          </Button>

          <div className="space-y-1.5 text-center text-sm text-muted-foreground">
            <div>
              Need a new code?{' '}
              <button
                type="button"
                onClick={resend}
                disabled={cooldown > 0}
                className="font-medium text-foreground underline-offset-4 hover:underline disabled:cursor-not-allowed disabled:opacity-50"
              >
                {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend'}
              </button>
            </div>
            {resend_error && <p className="text-xs text-destructive">{resend_error}</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
