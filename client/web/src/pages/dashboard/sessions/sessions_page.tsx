import { useEffect } from 'react'
import { Globe, Monitor, Clock, CalendarDays } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { load_sessions } from '@/controllers/dashboard_controller'
import { use_dashboard_store } from '@/store/dashboard_store'
import { use_auth_store } from '@/store/auth_store'
import type { UserSessionItem } from '@/types/api_types'
import { useState } from 'react'

function format_date(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function SessionCard({ session, is_current }: { session: UserSessionItem; is_current: boolean }) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-lg border p-4 transition-colors hover:bg-muted/30">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-muted">
          <Monitor className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="min-w-0 space-y-1">
          <div className="flex items-center gap-2">
            <p className="truncate text-sm font-medium">{session.device || 'Unknown device'}</p>
            {is_current && (
              <Badge variant="secondary" className="shrink-0 text-xs">
                Current
              </Badge>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Globe className="h-3 w-3" />
              {session.country}
            </span>
            <span className="flex items-center gap-1">
              <CalendarDays className="h-3 w-3" />
              Started {format_date(session.created_at)}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Expires {format_date(session.expires_at)}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export function SessionsPage() {
  const sessions = use_dashboard_store((s) => s.sessions)
  const current_user = use_auth_store((s) => s.user)
  const [loading, set_loading] = useState(true)

  useEffect(() => {
    load_sessions().finally(() => set_loading(false))
  }, [])

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Active Sessions</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          All devices currently signed in to your account.
        </p>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-medium">Sessions</CardTitle>
          <CardDescription>
            You have {sessions.length} active {sessions.length === 1 ? 'session' : 'sessions'}.
          </CardDescription>
        </CardHeader>
        <Separator />
        <CardContent className="pt-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : sessions.length === 0 ? (
            <p className="py-12 text-center text-sm text-muted-foreground">No active sessions found.</p>
          ) : (
            <div className="divide-y">
              {sessions.map((session) => (
                <div key={session.session_id} className="py-1 first:pt-4 last:pb-4">
                  <SessionCard
                    session={session}
                    is_current={session.session_id === current_user?.session_id}
                  />
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
