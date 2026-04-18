import { useEffect, useState } from 'react'
import { Smartphone, CalendarDays, Clock, Trash2 } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
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
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { handle_delete_devices, load_devices } from '@/controllers/dashboard_controller'
import { use_dashboard_store } from '@/store/dashboard_store'
import type { UserDeviceItem } from '@/types/api_types'

function format_date(iso: string | null): string {
  if (!iso) return 'Never'
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

interface DeviceRowProps {
  device: UserDeviceItem
  on_delete: (id: string) => Promise<void>
}

function DeviceRow({ device, on_delete }: DeviceRowProps) {
  const [deleting, set_deleting] = useState(false)

  const handle_confirm = async () => {
    set_deleting(true)
    try {
      await on_delete(device.device_id)
    } finally {
      set_deleting(false)
    }
  }

  return (
    <div className="flex items-center justify-between gap-4 py-4">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-muted">
          <Smartphone className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="space-y-1">
          <p className="text-sm font-medium">{device.device_name ?? 'Unknown device'}</p>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <CalendarDays className="h-3 w-3" />
              Added {format_date(device.created_at)}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {device.expires_at ? `Expires ${format_date(device.expires_at)}` : (
                <Badge variant="secondary" className="text-xs">Never expires</Badge>
              )}
            </span>
          </div>
        </div>
      </div>

      <AlertDialog>
        <AlertDialogTrigger asChild>
          <Button variant="ghost" size="sm" className="shrink-0 text-muted-foreground hover:text-destructive">
            {deleting ? <LoadingSpinner size="sm" /> : <Trash2 className="h-4 w-4" />}
          </Button>
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove trusted device?</AlertDialogTitle>
            <AlertDialogDescription>
              This device will no longer be trusted and will require OTP verification on next login.
              All sessions associated with this device will be terminated.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handle_confirm}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Remove device
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

export function DevicesPage() {
  const devices = use_dashboard_store((s) => s.devices)
  const [loading, set_loading] = useState(true)

  useEffect(() => {
    load_devices().finally(() => set_loading(false))
  }, [])

  const on_delete = async (device_id: string) => {
    await handle_delete_devices([device_id])
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Trusted Devices</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Devices that can bypass OTP verification on login.
        </p>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-medium">Devices</CardTitle>
          <CardDescription>
            {devices.length} trusted {devices.length === 1 ? 'device' : 'devices'} on your account.
          </CardDescription>
        </CardHeader>
        <Separator />
        <CardContent className="pt-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : devices.length === 0 ? (
            <p className="py-12 text-center text-sm text-muted-foreground">No trusted devices.</p>
          ) : (
            <div className="divide-y">
              {devices.map((device) => (
                <DeviceRow key={device.device_id} device={device} on_delete={on_delete} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
