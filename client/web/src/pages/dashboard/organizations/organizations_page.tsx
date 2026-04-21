import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, ChevronRight, MoreHorizontal, Plus, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import {
  create_organization,
  edit_organization,
  initiate_organization_delete,
  leave_organization,
  load_organization_members,
  load_organizations,
  transfer_organization,
} from '@/controllers/core_controller'
import { core_routes } from '@/lib/constants'
import { use_core_store } from '@/store/core_store'
import type { OrganizationListItem } from '@/types/core_types'

type DialogMode = 'create' | 'rename' | 'transfer' | 'leave' | 'delete' | null

export function OrganizationsPage() {
  const navigate = useNavigate()
  const organizations = use_core_store((s) => s.organizations)
  const members_by_org = use_core_store((s) => s.members_by_org)
  const [loading, set_loading] = useState(true)
  const [dialog_mode, set_dialog_mode] = useState<DialogMode>(null)
  const [active_org, set_active_org] = useState<OrganizationListItem | null>(null)
  const [name, set_name] = useState('')
  const [confirmation_name, set_confirmation_name] = useState('')
  const [selected_member_id, set_selected_member_id] = useState('')
  const [error, set_error] = useState<string | null>(null)
  const [saving, set_saving] = useState(false)

  useEffect(() => {
    load_organizations()
      .catch(() => undefined)
      .finally(() => set_loading(false))
  }, [])

  const transfer_candidates = useMemo(() => {
    if (!active_org) return []
    return (members_by_org[active_org.organization_id] ?? []).filter((member) => member.user_id !== active_org.owner_user_id)
  }, [active_org, members_by_org])

  const open_dialog = async (mode: DialogMode, organization: OrganizationListItem | null = null) => {
    set_dialog_mode(mode)
    set_active_org(organization)
    set_error(null)
    set_name(mode === 'rename' && organization ? organization.name : '')
    set_confirmation_name('')
    set_selected_member_id('')

    if (mode === 'transfer' && organization) {
      try {
        await load_organization_members(organization.organization_id)
      } catch (err) {
        set_error(err instanceof Error ? err.message : 'Failed to load organization members.')
      }
    }
  }

  const close_dialog = () => {
    set_dialog_mode(null)
    set_active_org(null)
    set_name('')
    set_confirmation_name('')
    set_selected_member_id('')
    set_error(null)
    set_saving(false)
  }

  const submit = async () => {
    set_error(null)
    set_saving(true)
    try {
      if (dialog_mode === 'create') {
        const organization_id = await create_organization(name)
        close_dialog()
        navigate(core_routes.organization_members(organization_id))
        return
      }

      if (!active_org) return

      if (dialog_mode === 'rename') {
        await edit_organization(active_org.organization_id, name)
      } else if (dialog_mode === 'transfer') {
        await transfer_organization(active_org.organization_id, selected_member_id, confirmation_name)
      } else if (dialog_mode === 'leave') {
        await leave_organization(active_org.organization_id)
      } else if (dialog_mode === 'delete') {
        await initiate_organization_delete(active_org.organization_id)
        close_dialog()
        navigate(core_routes.organization_delete_verify(active_org.organization_id))
        return
      }

      close_dialog()
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
      set_saving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6 px-6 py-6 lg:px-8 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight leading-tight text-foreground">Organizations</h1>
          <p className="text-[13px] text-muted-foreground mt-1">Manage your organizations and workspaces.</p>
        </div>
        <Button onClick={() => open_dialog('create')} size="sm" className="h-8 text-xs font-bold px-3">
          <Plus className="h-3.5 w-3.5 mr-1.5" />
          New Organization
        </Button>
      </div>

      {organizations.length === 0 ? (
        <div className="max-w-lg rounded-lg border border-border/50 bg-card/30 p-12 text-center">
          <Building2 className="mx-auto h-10 w-10 text-muted-foreground/40 mb-4" />
          <h3 className="text-sm font-semibold">No organizations yet</h3>
          <p className="mt-1 text-xs text-muted-foreground">Create your first workspace to get started.</p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-2">
          {organizations.map((org) => {
            const owner = org.current_user_role === 'owner'
            return (
              <div
                key={org.organization_id}
                onClick={() => navigate(core_routes.organization_members(org.organization_id))}
                className="group relative flex flex-col justify-between rounded-lg border border-border/50 bg-card/40 p-4 hover:border-primary/30 hover:bg-accent/5 transition-all cursor-pointer shadow-sm"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-2 rounded-md bg-primary/10 border border-primary/20 group-hover:scale-105 transition-transform">
                      <Building2 className="h-3.5 w-3.5 text-primary" strokeWidth={2} />
                    </div>
                    <div className="flex items-center gap-1.5">
                      {owner && <Badge variant="outline" className="text-[9px] font-bold uppercase tracking-wider py-0 px-1.5 h-4.5 bg-primary/5 text-primary border-primary/20">Owner</Badge>}
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                          <Button variant="ghost" size="icon" className="h-7 w-7 opacity-0 group-hover:opacity-100">
                            <MoreHorizontal className="h-3.5 w-3.5" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="text-xs">
                          {owner && <DropdownMenuItem onClick={() => open_dialog('rename', org)}>Rename</DropdownMenuItem>}
                          {owner && <DropdownMenuItem onClick={() => open_dialog('transfer', org)}>Transfer ownership</DropdownMenuItem>}
                          {!owner && <DropdownMenuItem onClick={() => open_dialog('leave', org)}>Leave organization</DropdownMenuItem>}
                          {owner && (
                            <DropdownMenuItem className="text-destructive font-semibold" onClick={() => open_dialog('delete', org)}>
                              Delete
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                  <h3 className="text-[14px] font-bold tracking-tight text-foreground line-clamp-1">{org.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <p className="text-[10px] text-muted-foreground font-mono truncate uppercase tracking-widest bg-muted/30 px-1.5 py-0.5 rounded">
                      {org.organization_id.slice(0, 16)}
                    </p>
                  </div>
                </div>
                <div className="mt-5 flex items-center justify-between border-t border-border/20 pt-3">
                   <div className="flex items-center gap-1.5">
                      <Users className="h-3 w-3 text-muted-foreground/60" />
                      <span className="text-[10px] text-muted-foreground/60 font-bold uppercase tracking-wider">Active Workspace</span>
                   </div>
                   <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/40 group-hover:text-primary transition-colors" />
                </div>
              </div>
            )
          })}
        </div>
      )}

      <Dialog open={dialog_mode !== null} onOpenChange={(open) => !open && close_dialog()}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {dialog_mode === 'create' && 'Create organization'}
              {dialog_mode === 'rename' && 'Rename organization'}
              {dialog_mode === 'transfer' && 'Transfer ownership'}
              {dialog_mode === 'leave' && 'Leave organization'}
              {dialog_mode === 'delete' && 'Delete organization'}
            </DialogTitle>
            <DialogDescription>
              {dialog_mode === 'create' && 'Set up a new organization for your team and projects.'}
              {dialog_mode === 'rename' && 'Update the organization name.'}
              {dialog_mode === 'transfer' && 'Select a member and type the exact organization name to confirm ownership transfer.'}
              {dialog_mode === 'leave' && 'You will lose access to this organization immediately.'}
              {dialog_mode === 'delete' && 'We will send an OTP to your email to confirm permanent deletion.'}
            </DialogDescription>
          </DialogHeader>

          {(dialog_mode === 'create' || dialog_mode === 'rename') && (
            <div className="space-y-2">
              <Label htmlFor="org_name">Organization name</Label>
              <Input id="org_name" value={name} onChange={(e) => set_name(e.target.value)} autoFocus />
            </div>
          )}

          {dialog_mode === 'transfer' && active_org && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="member_select">Transfer to</Label>
                <select
                  id="member_select"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={selected_member_id}
                  onChange={(e) => set_selected_member_id(e.target.value)}
                >
                  <option value="">Select a member</option>
                  {transfer_candidates.map((member) => (
                    <option key={member.user_id} value={member.user_id}>
                      {member.name ?? member.email} ({member.role})
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm_org_name">Type {active_org.name} to confirm</Label>
                <Input
                  id="confirm_org_name"
                  value={confirmation_name}
                  onChange={(e) => set_confirmation_name(e.target.value)}
                />
              </div>
            </div>
          )}

          {dialog_mode === 'leave' && active_org && (
            <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
              You are about to leave <span className="font-medium">{active_org.name}</span>.
            </div>
          )}

          {dialog_mode === 'delete' && active_org && (
            <div className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              This will permanently delete <span className="font-medium">{active_org.name}</span> after OTP confirmation.
            </div>
          )}

          <ErrorAlert message={error} />

          <DialogFooter>
            <Button variant="outline" onClick={close_dialog}>Cancel</Button>
            <Button
              variant={dialog_mode === 'delete' ? 'destructive' : 'default'}
              onClick={submit}
              disabled={
                saving ||
                ((dialog_mode === 'create' || dialog_mode === 'rename') && name.trim().length < 2) ||
                (dialog_mode === 'transfer' && (!selected_member_id || confirmation_name.trim() !== active_org?.name))
              }
            >
              {saving && <LoadingSpinner size="sm" className="text-primary-foreground" />}
              {dialog_mode === 'delete' ? 'Send verification code' : 'Continue'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
