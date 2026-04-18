import { useEffect, useState } from 'react'
import { CalendarDays, Mail, Shield, User, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
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
    <div className="flex items-center justify-between py-3">
      <div className="flex items-center gap-3 text-sm text-muted-foreground">
        {icon}
        {label}
      </div>
      <div className="text-sm font-medium">{value}</div>
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
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="p-8">
        <p className="text-sm text-muted-foreground">Failed to load profile.</p>
      </div>
    )
  }

  const initials = profile.name
    ? profile.name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : profile.email.slice(0, 2).toUpperCase()

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Profile</h1>
        <p className="mt-1 text-sm text-muted-foreground">Your account information.</p>
      </div>

      <div className="space-y-6">
        {/* Avatar card */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <Avatar className="h-16 w-16">
                {profile.avatar_url && (
                  <AvatarImage src={profile.avatar_url} alt={profile.name ?? profile.email} />
                )}
                <AvatarFallback className="text-lg font-semibold">{initials}</AvatarFallback>
              </Avatar>
              <div>
                <p className="text-lg font-semibold">{profile.name ?? 'No name set'}</p>
                <p className="text-sm text-muted-foreground">{profile.email}</p>
                <div className="mt-2 flex gap-2">
                  <Badge variant="secondary" className="capitalize">
                    {profile.account_plan}
                  </Badge>
                  <Badge
                    variant={profile.account_status === 'active' ? 'default' : 'destructive'}
                    className="capitalize"
                  >
                    {profile.account_status}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Details card */}
        <Card>
          <CardHeader className="pb-0">
            <CardTitle className="text-base font-medium">Account Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="divide-y">
              <InfoRow
                icon={<Mail className="h-4 w-4" />}
                label="Email"
                value={profile.email}
              />
              <InfoRow
                icon={<User className="h-4 w-4" />}
                label="Name"
                value={profile.name ?? <span className="text-muted-foreground">Not set</span>}
              />
              <InfoRow
                icon={<Shield className="h-4 w-4" />}
                label="Auth provider"
                value={provider_label(profile.provider)}
              />
              <InfoRow
                icon={<Zap className="h-4 w-4" />}
                label="Plan"
                value={<span className="capitalize">{profile.account_plan}</span>}
              />
              <InfoRow
                icon={<CalendarDays className="h-4 w-4" />}
                label="Member since"
                value={format_date(profile.created_at)}
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
