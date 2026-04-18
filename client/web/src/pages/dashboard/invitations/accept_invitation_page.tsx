import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorAlert } from '@/components/shared/error_alert'
import { accept_invitation } from '@/controllers/core_controller'
import { ROUTES } from '@/lib/constants'

export function AcceptInvitationPage() {
  const navigate = useNavigate()
  const [invitation_key, set_invitation_key] = useState('')
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    set_error(null)
    set_loading(true)
    try {
      await accept_invitation(invitation_key)
      navigate(ROUTES.DASHBOARD_ORGANIZATIONS, { replace: true })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      set_loading(false)
    }
  }

  return (
    <div className="p-8">
      <Card className="max-w-md">
        <CardHeader className="space-y-1 pb-4">
          <CardTitle className="text-2xl font-semibold">Accept invitation</CardTitle>
          <CardDescription>Paste the invitation code from email to join an organization.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={submit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="invitation_key">Invitation code</Label>
              <Input id="invitation_key" value={invitation_key} onChange={(e) => set_invitation_key(e.target.value)} />
            </div>
            <ErrorAlert message={error} />
            <Button type="submit" disabled={loading || invitation_key.trim().length < 6}>Join organization</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
