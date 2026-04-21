import { useEffect, useState } from 'react'
import { CalendarDays, Mail, Shield, User, Zap } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { load_profile } from '@/controllers/dashboard_controller'
import { use_dashboard_store } from '@/store/dashboard_store'

function format_date(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
}

function provider_label(provider: string): string {
  const labels: Record<string, string> = {
    email: 'Email / Password',
    google: 'Google',
    github: 'GitHub',
  }
  return labels[provider] ?? provider
}

interface InfoRowProps {
  icon: React.ReactNode
  label: string
  value: React.ReactNode
}

function InfoRow({ icon, label, value }: InfoRowProps) {
  return (
    <div className="flex items-center justify-between py-2.5 px-1.5 hover:bg-accent/5 transition-colors rounded-sm">
      <div className="flex items-center gap-2.5 text-[12px] font-bold uppercase tracking-wider text-muted-foreground/60">
        <span className="text-muted-foreground/40">{icon}</span>
        {label}
      </div>
      <div className="text-[13px] font-bold text-foreground">{value}</div>
    </div>
  )
}

export function ProfilePage() {
  const profile = use_dashboard_store((s) => s.profile)
  const [loading, set_loading] = useState(true)

  useEffect(() => {
    load_profile().finally(() => set_loading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner size="sm" />
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="p-8 max-w-5xl">
        <p className="text-xs text-muted-foreground">Failed to load account profile.</p>
      </div>
    )
  }

  const initials = profile.name
    ? profile.name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
    : profile.email.slice(0, 2).toUpperCase()

  return (
    <div className="space-y-6 px-6 py-6 lg:px-8 max-w-5xl">
       <div className="mb-6 flex flex-col gap-1">
          <h1 className="text-xl font-bold tracking-tight leading-tight text-foreground">Account Profile</h1>
          <p className="text-[13px] text-muted-foreground">Your personal identity and security settings.</p>
       </div>

      <div className="space-y-6">
        <div className="rounded-lg border border-border/50 bg-card/40 p-5 flex items-center gap-5 shadow-sm">
           <Avatar className="h-14 w-14 border border-border/50 shadow-sm">
            {profile.avatar_url && (
              <AvatarImage src={profile.avatar_url} alt={profile.name ?? profile.email} />
            )}
            <AvatarFallback className="text-sm font-black bg-primary/10 text-primary">{initials}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
             <div className="flex items-center gap-3">
               <p className="text-lg font-bold tracking-tight text-foreground truncate leading-none mb-1">{profile.name ?? 'Anonymous User'}</p>
               <Badge className="h-4 px-1.5 text-[8px] font-black uppercase tracking-tighter bg-primary/20 text-primary border-primary/20">
                 {profile.account_plan}
               </Badge>
             </div>
             <p className="text-[12px] text-muted-foreground font-medium">{profile.email}</p>
          </div>
          <Badge
            variant={profile.account_status === 'active' ? 'outline' : 'destructive'}
            className="text-[9px] font-black uppercase tracking-widest px-2"
          >
            {profile.account_status}
          </Badge>
        </div>

        <div className="rounded-lg border border-border/50 bg-card/40 overflow-hidden shadow-sm">
          <div className="bg-muted/30 px-5 py-2.5 border-b border-border/50 text-[10px] uppercase font-bold tracking-widest text-muted-foreground/60">
             Identity Details
          </div>
          <div className="p-4 space-y-1 divide-y divide-border/20">
              <InfoRow
                icon={<Mail className="h-3.5 w-3.5" />}
                label="Primary Email"
                value={profile.email}
              />
              <InfoRow
                icon={<User className="h-3.5 w-3.5" />}
                label="Full Name"
                value={profile.name ?? <span className="text-muted-foreground/40 italic">Not specified</span>}
              />
              <InfoRow
                icon={<Shield className="h-3.5 w-3.5" />}
                label="Auth Provider"
                value={provider_label(profile.provider)}
              />
              <InfoRow
                icon={<Zap className="h-3.5 w-3.5" />}
                label="Subscription"
                value={<span className="capitalize">{profile.account_plan}</span>}
              />
              <InfoRow
                icon={<CalendarDays className="h-3.5 w-3.5" />}
                label="Registration Date"
                value={format_date(profile.created_at)}
              />
          </div>
        </div>
      </div>
    </div>
  )
}
