import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { MailPlus, MoreHorizontal } from 'lucide-react'
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
    <div className="space-y-6 max-w-5xl">
       <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-lg border border-border/50 bg-card/20 p-4">
           <h3 className="text-[13px] font-bold uppercase tracking-[0.05em] text-muted-foreground/60 mb-2">Accept Invitation</h3>
           <div className="flex gap-2">
             <Input
                placeholder="Paste code from email"
                value={invitation_key}
                onChange={(e) => set_invitation_key(e.target.value)}
                className="h-8 text-xs bg-background"
              />
              <Button size="sm" className="h-8 text-xs px-3 font-bold" onClick={handle_accept} disabled={saving || invitation_key.trim().length < 6}>
                Join
              </Button>
           </div>
        </div>

        <div className="rounded-lg border border-border/50 bg-card/20 p-4 flex items-center justify-between">
           <div>
             <h3 className="text-[13px] font-bold uppercase tracking-[0.05em] text-muted-foreground/60">Invite Member</h3>
             <p className="text-[11px] text-muted-foreground mt-0.5">Add someone to your workspace team.</p>
           </div>
           {(current_role === 'owner' || current_role === 'admin') && (
            <Button size="sm" className="h-8 text-xs px-4 font-bold" onClick={() => set_invite_open(true)}>
              <MailPlus className="h-3.5 w-3.5 mr-1.5" />
              Invite
            </Button>
          )}
        </div>
      </div>

      <div className="rounded-lg border border-border/50 bg-card/40 overflow-hidden">
        <div className="grid grid-cols-12 bg-muted/30 px-5 py-2.5 border-b border-border/50 text-[10px] uppercase font-bold tracking-widest text-muted-foreground/80">
           <div className="col-span-6">Member</div>
           <div className="col-span-4 text-center">Status / Role</div>
           <div className="col-span-2 text-right pr-2">Actions</div>
        </div>

        <div className="divide-y divide-border/30">
          {loading ? (
             <div className="flex items-center justify-center py-12"><LoadingSpinner size="sm" /></div>
          ) : members.length === 0 ? (
             <div className="py-12 text-center text-xs text-muted-foreground">No members found.</div>
          ) : (
            members.map((member) => {
               const is_self = member.user_id === current_user?.user_id
               const can_promote = !is_self && member.role === 'member' && (current_role === 'owner' || current_role === 'admin')
               const can_demote = !is_self && member.role === 'admin' && current_role === 'owner'
               const can_remove = !is_self && ((current_role === 'owner' && member.role !== 'owner') || (current_role === 'admin' && member.role === 'member'))

               return (
                <div key={member.organization_member_id} className="grid grid-cols-12 items-center px-5 py-3 hover:bg-accent/5 transition-all text-xs">
                   <div className="col-span-6 flex items-center gap-3">
                      <div className="h-7 w-7 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-[10px] font-bold text-primary">
                         {member.email.slice(0, 2).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <p className="font-bold truncate text-foreground">{member.name ?? member.email}</p>
                        <p className="text-[10px] text-muted-foreground/70 truncate uppercase font-medium tracking-tight">Active since {new Date().toLocaleDateString()}</p>
                      </div>
                   </div>

                   <div className="col-span-4 flex items-center justify-center gap-3">
                      {is_self && <Badge variant="outline" className="h-5 px-1.5 text-[9px] font-black uppercase tracking-tighter bg-muted/30 border-muted-foreground/20 text-muted-foreground">You</Badge>}
                      {member.role === 'owner' && <Badge className="h-5 px-1.5 text-[9px] font-black uppercase tracking-tighter bg-primary/20 text-primary border-primary/20">Owner</Badge>}
                      {member.role === 'admin' && <Badge variant="secondary" className="h-5 px-1.5 text-[9px] font-black uppercase tracking-tighter italic">Admin</Badge>}
                      {member.role === 'member' && <Badge variant="outline" className="h-5 px-1.5 text-[9px] font-black uppercase tracking-tighter">Member</Badge>}
                   </div>

                   <div className="col-span-2 text-right">
                     {(can_promote || can_demote || can_remove) && (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-7 w-7 transition-colors">
                              <MoreHorizontal className="h-3.5 w-3.5" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="text-xs">
                            {can_promote && <DropdownMenuItem onClick={() => run_action(() => promote_member(organizationId, member.user_id))}>Promote to admin</DropdownMenuItem>}
                            {can_demote && <DropdownMenuItem onClick={() => run_action(() => demote_member(organizationId, member.user_id))}>Demote to member</DropdownMenuItem>}
                            {can_remove && (
                              <DropdownMenuItem className="text-destructive font-semibold" onClick={() => run_action(() => remove_member(organizationId, member.user_id))}>
                                Remove member
                              </DropdownMenuItem>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      )}
                   </div>
                </div>
               )
            })
          )}
        </div>
      </div>

      {invitations.length > 0 && (
        <div className="rounded-lg border border-border/50 bg-card/10 overflow-hidden mt-8">
           <div className="bg-muted/30 px-5 py-2 border-b border-border/50 text-[10px] uppercase font-bold tracking-widest text-muted-foreground/60">
             Pending Invitations
           </div>
           <div className="divide-y divide-border/30">
              {invitations.map((invitation) => (
                <div key={invitation.invitation_id} className="flex items-center justify-between px-5 py-3 text-xs">
                   <div className="flex items-center gap-3">
                      <div className="h-7 w-7 rounded-full bg-muted border flex items-center justify-center">
                         <MailPlus className="h-3 w-3 text-muted-foreground" />
                      </div>
                      <div>
                        <p className="font-bold">{invitation.email}</p>
                        <p className="text-[10px] text-muted-foreground/70 uppercase">Role: {invitation.role}</p>
                      </div>
                   </div>
                   {(current_role === 'owner' || current_role === 'admin') && (
                    <Button variant="ghost" size="sm" className="h-7 text-[10px] text-destructive hover:bg-destructive/5 font-bold px-3" onClick={() => run_action(() => cancel_invitation(organizationId, invitation.invitation_id))}>
                      Cancel
                    </Button>
                  )}
                </div>
              ))}
           </div>
        </div>
      )}

      <Dialog open={invite_open} onOpenChange={set_invite_open}>
        <DialogContent className="max-w-md p-6">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold tracking-tight">Invite member</DialogTitle>
            <DialogDescription className="text-xs">Send an invitation email to join this organization workspace.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div className="space-y-1.5">
              <Label htmlFor="invite_email" className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Email Address</Label>
              <Input id="invite_email" type="email" placeholder="dev@authkit.io" value={invite_email} onChange={(e) => set_invite_email(e.target.value)} className="h-9 text-xs" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="invite_role" className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Workspace Role</Label>
              <select
                id="invite_role"
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs shadow-sm transition-colors focus:ring-1 focus:ring-primary"
                value={invite_role}
                onChange={(e) => set_invite_role(e.target.value as 'admin' | 'member')}
              >
                <option value="member">Member (Read/Write)</option>
                {current_role === 'owner' && <option value="admin">Admin (Full Control)</option>}
              </select>
            </div>
          </div>
          <ErrorAlert message={error} />
          <DialogFooter className="mt-6">
            <Button variant="ghost" size="sm" className="text-xs font-bold" onClick={() => set_invite_open(false)}>Cancel</Button>
            <Button size="sm" className="text-xs font-bold px-5" onClick={handle_invite} disabled={saving || invite_email.trim().length < 3}>
              {saving ? <LoadingSpinner size="sm" /> : "Send invitation"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ErrorAlert message={error} />
    </div>
  )
}
