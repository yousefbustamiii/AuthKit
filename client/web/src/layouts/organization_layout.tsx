import { useEffect } from 'react'
import { NavLink, Navigate, Outlet, useParams } from 'react-router-dom'
import { Building2, CreditCard, FolderKanban, Users } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import { core_routes, ROUTES } from '@/lib/constants'
import { load_organizations } from '@/controllers/core_controller'
import { use_core_store } from '@/store/core_store'
import { cn } from '@/lib/utils'

function SectionLink({ to, label, icon }: { to: string; label: string; icon: React.ReactNode }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        cn(
          'inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-[13px] font-medium transition-colors border border-transparent',
          isActive ? 'bg-background text-foreground border-border shadow-sm' : 'text-muted-foreground hover:text-foreground',
        )
      }
    >
      <span className="scale-90">{icon}</span>
      {label}
    </NavLink>
  )
}

export function OrganizationLayout() {
  const { organizationId } = useParams<{ organizationId: string }>()
  const organizations = use_core_store((s) => s.organizations)
  const selected_organization_id = use_core_store((s) => s.selected_organization_id)
  const set_selected_organization_id = use_core_store((s) => s.set_selected_organization_id)

  useEffect(() => {
    if (organizations.length === 0) {
      load_organizations().catch(() => undefined)
    }
  }, [organizations.length])

  useEffect(() => {
    const next_organization_id = organizationId ?? null
    if (selected_organization_id !== next_organization_id) {
      set_selected_organization_id(next_organization_id)
    }
  }, [organizationId, selected_organization_id, set_selected_organization_id])

  if (!organizationId) {
    return <Navigate to={ROUTES.DASHBOARD_ORGANIZATIONS} replace />
  }

  const organization = organizations.find((item) => item.organization_id === organizationId)

  if (organizations.length === 0 && !organization) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!organization) {
    return <Navigate to={ROUTES.DASHBOARD_ORGANIZATIONS} replace />
  }

  return (
    <div className="px-6 py-6 lg:px-8 lg:py-6 max-w-6xl">
      <div className="mb-6 flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 shadow-sm">
              <Building2 className="h-4 w-4 text-primary" strokeWidth={2} />
            </div>
            <div>
              <h1 className="text-xl font-semibold tracking-tight leading-tight">{organization.name}</h1>
              <p className="text-[11px] font-medium text-muted-foreground/80 tracking-wide uppercase mt-0.5">Organization ID: {organization.organization_id}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-[10px] uppercase font-bold tracking-wider px-2 py-0 h-5">
              {organization.current_user_role}
            </Badge>
            <Button asChild variant="outline" size="sm" className="h-8 text-xs">
              <NavLink to={ROUTES.DASHBOARD_ORGANIZATIONS}>Back</NavLink>
            </Button>
          </div>
        </div>

        <div className="flex flex-wrap gap-1 border-b pb-1.5 mt-2">
          <SectionLink to={core_routes.organization_members(organizationId)} label="Members" icon={<Users className="h-3.5 w-3.5" />} />
          <SectionLink to={core_routes.organization_projects(organizationId)} label="Projects" icon={<FolderKanban className="h-3.5 w-3.5" />} />
          <SectionLink to={core_routes.organization_billing(organizationId)} label="Billing" icon={<CreditCard className="h-3.5 w-3.5" />} />
        </div>
      </div>

      <div className="animate-in fade-in slide-in-from-bottom-1 duration-300">
        <Outlet />
      </div>
    </div>
  )
}
