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
          'flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-[13px] font-medium transition-colors',
          isActive
            ? 'bg-accent text-accent-foreground shadow-sm'
            : 'text-muted-foreground hover:bg-accent/40 hover:text-foreground',
        )
      }
    >
      <span className="shrink-0 scale-90">{icon}</span>
      {label}
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
    <aside className="hidden md:flex h-full w-[240px] shrink-0 flex-col border-r bg-card/30 backdrop-blur-sm">
      {/* Brand */}
      <div className="flex h-12 items-center gap-2.5 px-5">
        <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary shadow-sm">
          <ShieldCheck className="h-3.5 w-3.5 text-primary-foreground" />
        </div>
        <span className="text-sm font-semibold tracking-tight">AuthKit</span>
      </div>

      {/* User info */}
      <div className="flex items-center gap-3 px-5 py-3.5">
        <Avatar className="h-7 w-7 border shadow-sm">
          <AvatarFallback className="text-[10px] font-semibold bg-muted">{initials}</AvatarFallback>
        </Avatar>
        <div className="min-w-0 flex-1">
          <p className="truncate text-xs font-semibold leading-none text-foreground">{user?.email ?? '—'}</p>
          <p className="mt-1 text-[10px] text-muted-foreground/70 uppercase tracking-wider font-bold leading-none">{user?.account_status ?? ''}</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-0.5 px-3 py-2">
        <div className="mt-2 mb-1.5 px-2.5 text-[10px] font-bold uppercase tracking-[0.1em] text-muted-foreground/50">
          Overview
        </div>
        <NavItem to={ROUTES.DASHBOARD} icon={<LayoutDashboard className="h-4 w-4" />} label="Sessions" />
        <NavItem to={ROUTES.DASHBOARD_ORGANIZATIONS} icon={<Building2 className="h-4 w-4" />} label="Organizations" />
        <NavItem to={ROUTES.DASHBOARD_PROFILE} icon={<User className="h-4 w-4" />} label="Profile" />
        <NavItem to={ROUTES.DASHBOARD_DEVICES} icon={<Smartphone className="h-4 w-4" />} label="Devices" />

        <div className="pt-5">
          <div className="mb-1.5 px-2.5 text-[10px] font-bold uppercase tracking-[0.1em] text-muted-foreground/50">
            Account Security
          </div>
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
    <div className="flex h-screen overflow-hidden bg-background selection:bg-primary/10">
      <SessionExpiredOverlay />
      <Sidebar />
      <main className="flex-1 overflow-auto bg-background/50">
        <div className="mx-auto max-w-6xl">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
