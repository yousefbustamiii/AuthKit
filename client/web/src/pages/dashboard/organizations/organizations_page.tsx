import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, Crown, MoreHorizontal, Plus, Users } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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

function format_date(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

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
    <div className="p-8">
      <div className="mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Organizations</h1>
          <p className="mt-1 text-sm text-muted-foreground">Create and manage your workspaces.</p>
        </div>
        <Button onClick={() => open_dialog('create')}>
          <Plus className="h-4 w-4" />
          New organization
        </Button>
      </div>

      {organizations.length === 0 ? (
        <Card className="max-w-lg">
          <CardContent className="flex flex-col items-center justify-center gap-3 py-12 text-center">
            <Building2 className="h-10 w-10 text-muted-foreground" />
            <div>
              <p className="text-base font-medium">No organizations yet</p>
              <p className="mt-1 text-sm text-muted-foreground">Create your first workspace to start inviting members, creating projects, and managing billing.</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {organizations.map((organization) => {
            const owner = organization.current_user_role === 'owner'
            return (
              <Card key={organization.organization_id}>
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <CardTitle className="text-lg">{organization.name}</CardTitle>
                      <CardDescription className="mt-1">Created {format_date(organization.created_at)}</CardDescription>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        {owner && <DropdownMenuItem onClick={() => open_dialog('rename', organization)}>Rename</DropdownMenuItem>}
                        {owner && <DropdownMenuItem onClick={() => open_dialog('transfer', organization)}>Transfer ownership</DropdownMenuItem>}
                        {!owner && <DropdownMenuItem onClick={() => open_dialog('leave', organization)}>Leave organization</DropdownMenuItem>}
                        {owner && (
                          <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={() => open_dialog('delete', organization)}>
                            Delete organization
                          </DropdownMenuItem>
                        )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary" className="capitalize">
                      {organization.current_user_role}
                    </Badge>
                    {owner ? (
                      <Badge className="gap-1"><Crown className="h-3 w-3" /> Owner</Badge>
                    ) : (
                      <Badge variant="outline" className="gap-1"><Users className="h-3 w-3" /> Member</Badge>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <Button onClick={() => navigate(core_routes.organization_members(organization.organization_id))}>Manage workspace</Button>
                    <Button variant="outline" onClick={() => navigate(core_routes.organization_billing(organization.organization_id))}>
                      Billing
                    </Button>
                  </div>
                </CardContent>
              </Card>
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
