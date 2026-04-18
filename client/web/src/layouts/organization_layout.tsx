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
          'inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors',
          isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground',
        )
      }
    >
      {icon}
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
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary">
                <Building2 className="h-5 w-5 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold tracking-tight">{organization.name}</h1>
                <p className="mt-1 text-sm text-muted-foreground">Manage members, projects, API keys, and billing.</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="secondary" className="capitalize">
              {organization.current_user_role}
            </Badge>
            <Button asChild variant="outline">
              <NavLink to={ROUTES.DASHBOARD_ORGANIZATIONS}>All organizations</NavLink>
            </Button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 border-b pb-3">
          <SectionLink to={core_routes.organization_members(organizationId)} label="Members" icon={<Users className="h-4 w-4" />} />
          <SectionLink to={core_routes.organization_projects(organizationId)} label="Projects" icon={<FolderKanban className="h-4 w-4" />} />
          <SectionLink to={core_routes.organization_billing(organizationId)} label="Billing" icon={<CreditCard className="h-4 w-4" />} />
        </div>
      </div>

      <Outlet />
    </div>
  )
}
