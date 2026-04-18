import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  User,
  Smartphone,
  Mail,
  Lock,
  Trash2,
  LogOut,
  ShieldCheck,
  ChevronRight,
  Building2,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { SessionExpiredOverlay } from '@/components/shared/session_expired_overlay'
import { ROUTES } from '@/lib/constants'
import { handle_logout } from '@/controllers/auth_controller'
import { use_auth_store } from '@/store/auth_store'

interface NavItemProps {
  to: string
  icon: React.ReactNode
  label: string
}

function NavItem({ to, icon, label }: NavItemProps) {
  return (
    <NavLink
      to={to}
      end={to === ROUTES.DASHBOARD}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
          isActive
            ? 'bg-accent text-accent-foreground'
            : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground',
        )
      }
    >
      {icon}
      {label}
      <ChevronRight className="ml-auto h-3.5 w-3.5 opacity-0 group-[.active]:opacity-100" />
    </NavLink>
  )
}

function Sidebar() {
  const navigate = useNavigate()
  const user = use_auth_store((s) => s.user)

  const initials = user?.email?.slice(0, 2).toUpperCase() ?? 'AU'

  const on_logout = async () => {
    try {
      await handle_logout()
    } finally {
      navigate(ROUTES.LOGIN, { replace: true })
    }
  }

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r bg-card">
      {/* Brand */}
      <div className="flex h-16 items-center gap-2.5 px-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <ShieldCheck className="h-4 w-4 text-primary-foreground" />
        </div>
        <span className="font-semibold tracking-tight">AuthKit</span>
      </div>

      <Separator />

      {/* User info */}
      <div className="flex items-center gap-3 px-4 py-4">
        <Avatar className="h-9 w-9">
          <AvatarFallback className="text-xs font-medium">{initials}</AvatarFallback>
        </Avatar>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium">{user?.email ?? '—'}</p>
          <p className="text-xs text-muted-foreground capitalize">{user?.account_status ?? ''}</p>
        </div>
      </div>

      <Separator />

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          Overview
        </p>
        <NavItem to={ROUTES.DASHBOARD} icon={<LayoutDashboard className="h-4 w-4" />} label="Sessions" />
        <NavItem to={ROUTES.DASHBOARD_ORGANIZATIONS} icon={<Building2 className="h-4 w-4" />} label="Organizations" />
        <NavItem to={ROUTES.DASHBOARD_PROFILE} icon={<User className="h-4 w-4" />} label="Profile" />
        <NavItem to={ROUTES.DASHBOARD_DEVICES} icon={<Smartphone className="h-4 w-4" />} label="Devices" />

        <div className="pt-4">
          <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Settings
          </p>
          <NavItem to={ROUTES.DASHBOARD_SETTINGS_EMAIL} icon={<Mail className="h-4 w-4" />} label="Change Email" />
          <NavItem to={ROUTES.DASHBOARD_SETTINGS_PASSWORD} icon={<Lock className="h-4 w-4" />} label="Change Password" />
          <NavItem to={ROUTES.DASHBOARD_SETTINGS_DELETE} icon={<Trash2 className="h-4 w-4" />} label="Delete Account" />
        </div>
      </nav>

      <Separator />

      {/* Logout */}
      <div className="p-3">
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 text-muted-foreground hover:text-foreground"
          onClick={on_logout}
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </Button>
      </div>
    </aside>
  )
}

export function DashboardLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <SessionExpiredOverlay />
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
