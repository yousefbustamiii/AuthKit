import { useEffect, useState } from 'react'
import { Smartphone, CalendarDays, Clock, Trash2 } from 'lucide-react'
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
    <div className="flex items-center justify-between gap-4 px-5 py-3 hover:bg-accent/5 transition-all group">
      <div className="flex items-center gap-3">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted/40 border border-border/50 group-hover:bg-primary/5 transition-colors">
          <Smartphone className="h-3.5 w-3.5 text-muted-foreground/60 group-hover:text-primary transition-colors" />
        </div>
        <div className="min-w-0">
          <p className="text-[13px] font-bold text-foreground truncate leading-tight">{device.device_name || 'Unknown device'}</p>
          <div className="flex items-center gap-2 mt-0.5 text-[10px] text-muted-foreground/60 font-medium uppercase tracking-tight">
            <span className="flex items-center gap-1">
              <CalendarDays className="h-2.5 w-2.5" />
              Reg: {format_date(device.created_at)}
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Clock className="h-2.5 w-2.5" />
              {device.expires_at ? `Exp: ${format_date(device.expires_at)}` : 'PERMANENT'}
            </span>
          </div>
        </div>
      </div>

      <AlertDialog>
        <AlertDialogTrigger asChild>
          <Button variant="ghost" size="icon" className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-all text-muted-foreground hover:text-destructive">
            {deleting ? <LoadingSpinner size="sm" /> : <Trash2 className="h-3.5 w-3.5" />}
          </Button>
        </AlertDialogTrigger>
        <AlertDialogContent className="max-w-md">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-lg font-bold tracking-tight">Revoke trusted status?</AlertDialogTitle>
            <AlertDialogDescription className="text-xs">
              This device will no longer be trusted and will require OTP verification on next login. All active sessions on this hardware will be terminated.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="mt-4">
            <AlertDialogCancel className="text-xs h-8">Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handle_confirm}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90 h-8 text-xs font-bold"
            >
              Confirm Revocation
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
    <div className="space-y-6 px-6 py-6 lg:px-8 max-w-5xl">
       <div className="mb-6 flex flex-col gap-1 text-left">
          <h1 className="text-xl font-bold tracking-tight leading-tight text-foreground">Trusted Devices</h1>
          <p className="text-[13px] text-muted-foreground">Manage hardware authorized to bypass two-factor authentication.</p>
       </div>

       <div className="rounded-lg border border-border/50 bg-card/40 overflow-hidden shadow-sm">
          <div className="bg-muted/30 px-5 py-2.5 border-b border-border/50 text-[10px] uppercase font-bold tracking-widest text-muted-foreground/60">
             Trusted Hardware ({devices.length})
          </div>
          <div className="divide-y divide-border/30">
            {loading ? (
               <div className="flex items-center justify-center py-12"><LoadingSpinner size="sm" /></div>
            ) : devices.length === 0 ? (
               <div className="py-12 text-center text-xs text-muted-foreground italic">No trusted devices found.</div>
            ) : (
               devices.map((device) => (
                <DeviceRow key={device.device_id} device={device} on_delete={on_delete} />
               ))
            )}
          </div>
       </div>
    </div>
  )
}
