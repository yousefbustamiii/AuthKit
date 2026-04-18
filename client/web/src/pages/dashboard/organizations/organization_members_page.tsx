import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Crown, MailPlus, MoreHorizontal, Shield, User } from 'lucide-react'
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
  accept_invitation,
  cancel_invitation,
  demote_member,
  invite_member,
  load_organization_invitations,
  load_organization_members,
  promote_member,
  remove_member,
} from '@/controllers/core_controller'
import { use_auth_store } from '@/store/auth_store'
import { use_core_store } from '@/store/core_store'
import { ROUTES } from '@/lib/constants'
import type { OrganizationInvitation, OrganizationMember } from '@/types/core_types'

const EMPTY_MEMBERS: OrganizationMember[] = []
const EMPTY_INVITATIONS: OrganizationInvitation[] = []

export function OrganizationMembersPage() {
  const navigate = useNavigate()
  const { organizationId = '' } = useParams<{ organizationId: string }>()
  const organizations = use_core_store((s) => s.organizations)
  const members = use_core_store((s) => s.members_by_org[organizationId] ?? EMPTY_MEMBERS)
  const invitations = use_core_store((s) => s.invitations_by_org[organizationId] ?? EMPTY_INVITATIONS)
  const current_user = use_auth_store((s) => s.user)
  const organization = organizations.find((item) => item.organization_id === organizationId)
  const current_role = organization?.current_user_role ?? 'member'

  const [loading, set_loading] = useState(true)
  const [invite_open, set_invite_open] = useState(false)
  const [invite_email, set_invite_email] = useState('')
  const [invite_role, set_invite_role] = useState<'admin' | 'member'>('member')
  const [invitation_key, set_invitation_key] = useState('')
  const [error, set_error] = useState<string | null>(null)
  const [saving, set_saving] = useState(false)

  useEffect(() => {
    Promise.all([
      load_organization_members(organizationId),
      load_organization_invitations(organizationId),
    ])
      .catch(() => undefined)
      .finally(() => set_loading(false))
  }, [organizationId])

  const handle_invite = async () => {
    set_error(null)
    set_saving(true)
    try {
      await invite_member(organizationId, invite_email, invite_role)
      set_invite_email('')
      set_invite_role('member')
      set_invite_open(false)
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      set_saving(false)
    }
  }

  const handle_accept = async () => {
    set_error(null)
    set_saving(true)
    try {
      await accept_invitation(invitation_key)
      navigate(ROUTES.DASHBOARD_ORGANIZATIONS, { replace: true })
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      set_saving(false)
    }
  }

  const run_action = async (runner: () => Promise<void>) => {
    set_error(null)
    try {
      await runner()
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-medium">Accept invitation</CardTitle>
          <CardDescription>Paste an invitation code from email to join another organization.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 md:flex-row">
          <Input
            placeholder="Invitation code"
            value={invitation_key}
            onChange={(e) => set_invitation_key(e.target.value)}
          />
          <Button onClick={handle_accept} disabled={saving || invitation_key.trim().length < 6}>
            Accept invitation
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <CardTitle className="text-base font-medium">Members</CardTitle>
              <CardDescription>{members.length} active members in this organization.</CardDescription>
            </div>
            {(current_role === 'owner' || current_role === 'admin') && (
              <Button onClick={() => set_invite_open(true)}>
                <MailPlus className="h-4 w-4" />
                Invite member
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-12"><LoadingSpinner size="lg" /></div>
          ) : (
            members.map((member) => {
              const is_self = member.user_id === current_user?.user_id
              const can_promote = !is_self && member.role === 'member' && (current_role === 'owner' || current_role === 'admin')
              const can_demote = !is_self && member.role === 'admin' && current_role === 'owner'
              const can_remove =
                !is_self &&
                ((current_role === 'owner' && member.role !== 'owner') ||
                  (current_role === 'admin' && member.role === 'member'))

              return (
                <div key={member.organization_member_id} className="flex items-center justify-between gap-4 rounded-lg border p-4">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="truncate text-sm font-medium">{member.name ?? member.email}</p>
                      {member.role === 'owner' && <Badge className="gap-1"><Crown className="h-3 w-3" /> Owner</Badge>}
                      {member.role === 'admin' && <Badge variant="secondary" className="gap-1"><Shield className="h-3 w-3" /> Admin</Badge>}
                      {member.role === 'member' && <Badge variant="outline" className="gap-1"><User className="h-3 w-3" /> Member</Badge>}
                      {is_self && <Badge variant="outline">You</Badge>}
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">{member.email}</p>
                  </div>

                  {(can_promote || can_demote || can_remove) && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        {can_promote && <DropdownMenuItem onClick={() => run_action(() => promote_member(organizationId, member.user_id))}>Promote to admin</DropdownMenuItem>}
                        {can_demote && <DropdownMenuItem onClick={() => run_action(() => demote_member(organizationId, member.user_id))}>Demote to member</DropdownMenuItem>}
                        {can_remove && (
                          <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={() => run_action(() => remove_member(organizationId, member.user_id))}>
                            Remove member
                          </DropdownMenuItem>
                        )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </div>
              )
            })
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-4">
          <CardTitle className="text-base font-medium">Pending invitations</CardTitle>
          <CardDescription>{invitations.length} open invitations.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {invitations.length === 0 ? (
            <p className="text-sm text-muted-foreground">No pending invitations.</p>
          ) : (
            invitations.map((invitation) => (
              <div key={invitation.invitation_id} className="flex items-center justify-between gap-4 rounded-lg border p-4">
                <div>
                  <p className="text-sm font-medium">{invitation.email}</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Role: <span className="capitalize">{invitation.role}</span>
                  </p>
                </div>
                {(current_role === 'owner' || current_role === 'admin') && (
                  <Button variant="outline" onClick={() => run_action(() => cancel_invitation(organizationId, invitation.invitation_id))}>
                    Cancel
                  </Button>
                )}
              </div>
            ))
          )}
        </CardContent>
      </Card>

      <Dialog open={invite_open} onOpenChange={set_invite_open}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Invite member</DialogTitle>
            <DialogDescription>Send an email invitation to join this organization.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="invite_email">Email</Label>
              <Input id="invite_email" type="email" value={invite_email} onChange={(e) => set_invite_email(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="invite_role">Role</Label>
              <select
                id="invite_role"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={invite_role}
                onChange={(e) => set_invite_role(e.target.value as 'admin' | 'member')}
              >
                <option value="member">Member</option>
                {current_role === 'owner' && <option value="admin">Admin</option>}
              </select>
            </div>
          </div>
          <ErrorAlert message={error} />
          <DialogFooter>
            <Button variant="outline" onClick={() => set_invite_open(false)}>Cancel</Button>
            <Button onClick={handle_invite} disabled={saving || invite_email.trim().length < 3}>
              Send invitation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ErrorAlert message={error} />
    </div>
  )
}
