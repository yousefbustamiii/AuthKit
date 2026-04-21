import { useEffect, useState } from 'react'
import { KeyRound, MoreHorizontal, Pencil, Plus, RefreshCcw, Shield, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { ErrorAlert } from '@/components/shared/error_alert'
import { LoadingSpinner } from '@/components/shared/loading_spinner'
import {
  create_api_key,
  create_project,
  delete_project,
  edit_project,
  load_organization_projects,
  load_project_api_keys,
  revoke_api_key,
  rotate_api_key,
} from '@/controllers/core_controller'
import { use_core_store } from '@/store/core_store'
import { useParams } from 'react-router-dom'
import type { OrganizationProject, ProjectApiKey } from '@/types/core_types'

type ProjectDialogMode = 'create' | 'rename' | 'delete' | null
const EMPTY_PROJECTS: OrganizationProject[] = []
const EMPTY_API_KEYS: ProjectApiKey[] = []

export function OrganizationProjectsPage() {
  const { organizationId = '' } = useParams<{ organizationId: string }>()
  const organizations = use_core_store((s) => s.organizations)
  const projects = use_core_store((s) => s.projects_by_org[organizationId] ?? EMPTY_PROJECTS)
  const api_keys_by_project = use_core_store((s) => s.api_keys_by_project)
  const organization = organizations.find((item) => item.organization_id === organizationId)
  const can_manage = organization?.current_user_role === 'owner' || organization?.current_user_role === 'admin'

  const [loading, set_loading] = useState(true)
  const [error, set_error] = useState<string | null>(null)
  const [dialog_mode, set_dialog_mode] = useState<ProjectDialogMode>(null)
  const [active_project, set_active_project] = useState<{ project_id: string; name: string } | null>(null)
  const [name, set_name] = useState('')
  const [expanded_project_id, set_expanded_project_id] = useState<string | null>(null)
  const [raw_key, set_raw_key] = useState<string | null>(null)
  const [api_key_name, set_api_key_name] = useState('')
  const [api_key_confirmation, set_api_key_confirmation] = useState('')
  const [api_action, set_api_action] = useState<{ type: 'create' | 'rotate' | 'revoke'; project_id: string; key_id?: string } | null>(null)

  useEffect(() => {
    load_organization_projects(organizationId)
      .catch(() => undefined)
      .finally(() => set_loading(false))
  }, [organizationId])

  const with_error = async (runner: () => Promise<void>) => {
    set_error(null)
    try {
      await runner()
    } catch (err) {
      set_error(err instanceof Error ? err.message : 'Something went wrong.')
    }
  }

  const toggle_project = async (project_id: string) => {
    if (expanded_project_id === project_id) {
      set_expanded_project_id(null)
      return
    }
    set_expanded_project_id(project_id)
    await with_error(() => load_project_api_keys(organizationId, project_id))
  }

  return (
    <div className="space-y-6 max-w-5xl">
       <div className="flex items-center justify-between mb-4">
          <div>
             <h3 className="text-[13px] font-bold uppercase tracking-[0.05em] text-muted-foreground/60">Projects ({projects.length})</h3>
             <p className="text-[11px] text-muted-foreground mt-0.5">Manage API access and keys for your applications.</p>
          </div>
          {can_manage && (
            <Button size="sm" className="h-8 text-xs px-4 font-bold" onClick={() => { set_dialog_mode('create'); set_name('') }}>
              <Plus className="h-3.5 w-3.5 mr-1.5" />
              New Project
            </Button>
          )}
       </div>

       <div className="rounded-lg border border-border/50 bg-card/40 overflow-hidden shadow-sm">
          {loading ? (
             <div className="flex items-center justify-center py-12"><LoadingSpinner size="sm" /></div>
          ) : projects.length === 0 ? (
             <div className="py-12 text-center text-xs text-muted-foreground italic">No projects found for this organization.</div>
          ) : (
            <div className="divide-y divide-border/30">
               {projects.map((project) => {
                  const api_keys = api_keys_by_project[project.project_id] ?? EMPTY_API_KEYS
                  const expanded = expanded_project_id === project.project_id
                  
                  return (
                    <div key={project.project_id} className="group">
                       <div className="flex items-center justify-between px-5 py-3 hover:bg-accent/5 transition-all text-xs">
                          <div className="flex items-center gap-4">
                             <div className="h-2 w-2 rounded-full bg-primary/30 group-hover:scale-125 transition-transform" />
                             <div>
                                <p className="font-bold text-foreground text-[14px] leading-tight">{project.name}</p>
                                <div className="flex items-center gap-2 mt-0.5">
                                   <p className="text-[10px] text-muted-foreground/60 font-mono scale-95">{project.project_id}</p>
                                   <span className="text-[10px] text-muted-foreground/40 font-bold">•</span>
                                   <p className="text-[10px] text-muted-foreground/60 font-bold uppercase tracking-wider">{api_keys.length} KEYS</p>
                                </div>
                             </div>
                          </div>

                          <div className="flex items-center gap-2">
                             <Button variant="outline" size="sm" className="h-7 text-[10px] font-bold px-3 transition-all" onClick={() => toggle_project(project.project_id)}>
                                <KeyRound className="h-3.5 w-3.5 mr-1.5" strokeWidth={2.5} />
                                {expanded ? 'Hide Keys' : 'API Keys'}
                             </Button>
                             {can_manage && (
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="icon" className="h-7 w-7 opacity-0 group-hover:opacity-100">
                                      <MoreHorizontal className="h-3.5 w-3.5" />
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end" className="text-xs font-semibold">
                                     <DropdownMenuItem onClick={() => { set_dialog_mode('rename'); set_active_project(project); set_name(project.name) }}>
                                       <Pencil className="mr-2 h-3.5 w-3.5" /> Rename
                                     </DropdownMenuItem>
                                     <DropdownMenuItem className="text-destructive font-bold" onClick={() => { set_dialog_mode('delete'); set_active_project(project); set_name('') }}>
                                       <Trash2 className="mr-2 h-3.5 w-3.5" /> Delete
                                     </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                             )}
                          </div>
                       </div>

                       {expanded && (
                          <div className="bg-muted/10 border-y border-border/20 px-8 py-5 animate-in slide-in-from-top-1 duration-200">
                             {can_manage && (
                                <div className="mb-6 flex items-end gap-3 max-w-2xl">
                                   <div className="flex-1 space-y-1.5">
                                      <Label className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest pl-1">New Key Label</Label>
                                      <Input placeholder="e.g. Production Web" value={api_key_name} onChange={(e) => set_api_key_name(e.target.value)} className="h-8 text-xs bg-background" />
                                   </div>
                                   <Button 
                                      size="sm" 
                                      className="h-8 text-[11px] font-bold px-4"
                                      onClick={async () => {
                                        await with_error(async () => {
                                          const next_raw_key = await create_api_key(organizationId, project.project_id, api_key_name)
                                          set_api_key_name('')
                                          set_raw_key(next_raw_key)
                                        })
                                      }}
                                      disabled={api_key_name.trim().length < 2}
                                   >
                                      Generate Key
                                   </Button>
                                </div>
                             )}

                             <div className="space-y-2">
                                {api_keys.length === 0 ? (
                                   <p className="text-[11px] text-muted-foreground italic text-center py-4 bg-background/50 rounded border border-dashed border-border/50">No API keys active for this project.</p>
                                ) : (
                                   api_keys.map((api_key) => (
                                      <div key={api_key.key_id} className="group/api flex items-center justify-between p-2.5 rounded border border-border/30 bg-background/50 hover:bg-background transition-all">
                                         <div className="flex items-center gap-3">
                                            <Shield className="h-3.5 w-3.5 text-muted-foreground/30" />
                                            <div>
                                               <p className="text-[12px] font-bold leading-tight">{api_key.name}</p>
                                               <p className="text-[10px] text-muted-foreground/60 font-mono mt-0.5 tracking-tight uppercase">
                                                 Last used: {api_key.last_used_at ? new Date(api_key.last_used_at).toLocaleDateString() : 'Never'}
                                               </p>
                                            </div>
                                            {api_key.rotated_at && <Badge variant="secondary" className="h-4 px-1 text-[8px] font-black uppercase bg-primary/10 text-primary border-primary/20 leading-none">ROTATED</Badge>}
                                         </div>
                                         {can_manage && (
                                            <div className="flex items-center gap-1 opacity-0 group-hover/api:opacity-100 transition-opacity">
                                               <Button variant="ghost" size="sm" className="h-6 text-[10px] font-bold" onClick={() => { set_api_action({ type: 'rotate', project_id: project.project_id, key_id: api_key.key_id }); set_api_key_confirmation('') }}>
                                                  <RefreshCcw className="h-3 w-3 mr-1" /> Rotate
                                               </Button>
                                               <Button variant="ghost" size="sm" className="h-6 text-[10px] font-bold text-destructive hover:bg-destructive/5" onClick={() => { set_api_action({ type: 'revoke', project_id: project.project_id, key_id: api_key.key_id }); set_api_key_confirmation('') }}>
                                                  <Trash2 className="h-3 w-3 mr-1" /> Revoke
                                               </Button>
                                            </div>
                                         )}
                                      </div>
                                   ))
                                )}
                             </div>
                          </div>
                       )}
                    </div>
                  )
               })}
            </div>
          )}
       </div>

       <Dialog open={dialog_mode !== null} onOpenChange={(open) => !open && set_dialog_mode(null)}>
        <DialogContent className="max-w-md p-6">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold tracking-tight">
              {dialog_mode === 'create' && 'Create Project'}
              {dialog_mode === 'rename' && 'Rename Project'}
              {dialog_mode === 'delete' && 'Delete Project'}
            </DialogTitle>
            <DialogDescription className="text-xs">
              {dialog_mode === 'delete'
                ? `Type "${active_project?.name}" below to confirm permanent deletion.`
                : 'Define a new project workspace for your API authentication tokens.'}
            </DialogDescription>
          </DialogHeader>

          {(dialog_mode === 'create' || dialog_mode === 'rename') && (
            <div className="space-y-1.5 pt-4">
              <Label htmlFor="project_name" className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Project Name</Label>
              <Input id="project_name" placeholder="e.g. Mobile App" value={name} onChange={(e) => set_name(e.target.value)} className="h-9 text-xs" />
            </div>
          )}

          {dialog_mode === 'delete' && active_project && (
            <div className="space-y-1.5 pt-4">
              <Label htmlFor="project_confirm" className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Confirm Deletion</Label>
              <Input id="project_confirm" placeholder={active_project.name} value={name} onChange={(e) => set_name(e.target.value)} className="h-9 text-xs" />
            </div>
          )}

          <ErrorAlert message={error} />

          <DialogFooter className="mt-6">
            <Button variant="ghost" size="sm" className="text-xs font-bold" onClick={() => set_dialog_mode(null)}>Cancel</Button>
            <Button
              variant={dialog_mode === 'delete' ? 'destructive' : 'default'}
              size="sm"
              className="text-xs font-bold px-5"
              onClick={() => with_error(async () => {
                if (dialog_mode === 'create') await create_project(organizationId, name)
                if (dialog_mode === 'rename' && active_project) await edit_project(organizationId, active_project.project_id, name)
                if (dialog_mode === 'delete' && active_project) await delete_project(organizationId, active_project.project_id, name)
                set_dialog_mode(null)
                set_active_project(null)
                set_name('')
              })}
              disabled={
                dialog_mode === 'delete'
                  ? name !== active_project?.name
                  : name.trim().length < 2
              }
            >
              Continue
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={api_action !== null} onOpenChange={(open) => !open && set_api_action(null)}>
        <DialogContent className="max-w-sm p-6">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold tracking-tight">Security Action</DialogTitle>
            <DialogDescription className="text-xs">
              {api_action?.type === 'rotate' ? 'Type "ROTATE" to confirm. This will invalidate existing keys.' : 'Type "REVOKE" to confirm permanent deletion.'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-1.5 pt-4">
            <Label htmlFor="api_confirmation" className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Confirmation Code</Label>
            <Input id="api_confirmation" value={api_key_confirmation} onChange={(e) => set_api_key_confirmation(e.target.value)} className="h-9 text-xs" />
          </div>
          <ErrorAlert message={error} />
          <DialogFooter className="mt-6">
            <Button variant="ghost" size="sm" className="text-xs font-bold" onClick={() => set_api_action(null)}>Cancel</Button>
            <Button
              variant={api_action?.type === 'revoke' ? 'destructive' : 'default'}
              size="sm"
              className="text-xs font-bold px-5"
              onClick={() => with_error(async () => {
                if (!api_action?.key_id) return
                if (api_action.type === 'rotate') {
                  const next_raw_key = await rotate_api_key(organizationId, api_action.project_id, api_action.key_id, api_key_confirmation)
                  set_raw_key(next_raw_key)
                } else {
                  await revoke_api_key(organizationId, api_action.project_id, api_action.key_id, api_key_confirmation)
                }
                set_api_action(null)
                set_api_key_confirmation('')
              })}
              disabled={
                (api_action?.type === 'rotate' && api_key_confirmation !== 'ROTATE') ||
                (api_action?.type === 'revoke' && api_key_confirmation !== 'REVOKE')
              }
            >
              Confirm Action
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={raw_key !== null} onOpenChange={(open) => !open && set_raw_key(null)}>
        <DialogContent className="max-w-md p-6">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold tracking-tight">Strategic API Secret</DialogTitle>
            <DialogDescription className="text-xs">This key is only visible once. Store it in a secure environment.</DialogDescription>
          </DialogHeader>
          <div className="rounded border bg-muted/20 p-4 mt-4 font-mono text-xs break-all border-border/50 text-foreground shadow-inner">{raw_key}</div>
          <DialogFooter className="mt-6">
            <Button size="sm" className="text-xs font-bold px-10" onClick={() => set_raw_key(null)}>Done</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ErrorAlert message={error} />
    </div>
  )
}
