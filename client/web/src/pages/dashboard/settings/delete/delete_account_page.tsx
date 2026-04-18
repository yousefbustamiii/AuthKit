import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { TriangleAlert, Trash2 } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { handle_account_delete_initiate } from '@/controllers/dashboard_controller'
import { ROUTES } from '@/lib/constants'
import type { OtpRouterState } from '@/types/auth_types'

export function DeleteAccountPage() {
  const navigate = useNavigate()
  const [loading, set_loading] = useState(false)
  const [error, set_error] = useState<string | null>(null)

  const handle_confirm = async () => {
    set_error(null)
    set_loading(true)
    try {
      await handle_account_delete_initiate()
      const state: OtpRouterState = { context: 'account_delete' }
      navigate(ROUTES.OTP, { state })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      set_loading(false)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Delete Account</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Permanently remove your account and all associated data.
        </p>
      </div>

      <Card className="max-w-md border-destructive/30">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-2">
            <TriangleAlert className="h-5 w-5 text-destructive" />
            <CardTitle className="text-base font-medium text-destructive">
              Danger zone
            </CardTitle>
          </div>
          <CardDescription>
            This action is permanent and cannot be undone.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ul className="space-y-1.5 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-muted-foreground" />
              All your account data will be permanently deleted
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-muted-foreground" />
              All active sessions will be immediately terminated
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-muted-foreground" />
              All trusted devices will be removed
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-muted-foreground" />
              This action cannot be reversed
            </li>
          </ul>

          <ErrorAlert message={error} />

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" className="w-full" disabled={loading}>
                {loading ? (
                  <LoadingSpinner size="sm" className="mr-2 text-destructive-foreground" />
                ) : (
                  <Trash2 className="mr-2 h-4 w-4" />
                )}
                Delete my account
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently delete your account, all your sessions, and all your data.
                  We will send a verification code to your email to confirm this action.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handle_confirm}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  Yes, delete my account
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>
    </div>
  )
}
