import { useEffect, useState } from 'react'
import { KeyRound, MoreHorizontal, Pencil, Plus, RefreshCcw, Trash2 } from 'lucide-react'
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
    <div className="space-y-6">
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <CardTitle className="text-base font-medium">Projects</CardTitle>
              <CardDescription>{projects.length} projects in this organization.</CardDescription>
            </div>
            {can_manage && (
              <Button onClick={() => { set_dialog_mode('create'); set_name('') }}>
                <Plus className="h-4 w-4" />
                New project
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-12"><LoadingSpinner size="lg" /></div>
          ) : projects.length === 0 ? (
            <p className="text-sm text-muted-foreground">No projects yet.</p>
          ) : (
            projects.map((project) => {
              const api_keys = api_keys_by_project[project.project_id] ?? EMPTY_API_KEYS
              const expanded = expanded_project_id === project.project_id

              return (
                <div key={project.project_id} className="rounded-lg border">
                  <div className="flex items-center justify-between gap-4 p-4">
                    <div>
                      <p className="text-sm font-medium">{project.name}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{api_keys.length} API keys loaded</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" onClick={() => toggle_project(project.project_id)}>
                        <KeyRound className="h-4 w-4" />
                        {expanded ? 'Hide API keys' : 'Manage API keys'}
                      </Button>
                      {can_manage && (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => { set_dialog_mode('rename'); set_active_project(project); set_name(project.name) }}>
                              <Pencil className="h-4 w-4" />
                              Rename
                            </DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={() => { set_dialog_mode('delete'); set_active_project(project); set_name('') }}>
                              <Trash2 className="h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      )}
                    </div>
                  </div>

                  {expanded && (
                    <div className="border-t px-4 py-4">
                      {can_manage && (
                        <div className="mb-4 flex flex-col gap-3 md:flex-row">
                          <Input placeholder="New API key name" value={api_key_name} onChange={(e) => set_api_key_name(e.target.value)} />
                          <Button
                            onClick={async () => {
                              await with_error(async () => {
                                const next_raw_key = await create_api_key(organizationId, project.project_id, api_key_name)
                                set_api_key_name('')
                                set_raw_key(next_raw_key)
                              })
                            }}
                            disabled={api_key_name.trim().length < 2}
                          >
                            Create API key
                          </Button>
                        </div>
                      )}

                      <div className="space-y-3">
                        {api_keys.length === 0 ? (
                          <p className="text-sm text-muted-foreground">No API keys for this project.</p>
                        ) : (
                          api_keys.map((api_key) => (
                            <div key={api_key.key_id} className="flex items-center justify-between gap-4 rounded-md border p-3">
                              <div>
                                <div className="flex items-center gap-2">
                                  <p className="text-sm font-medium">{api_key.name}</p>
                                  {api_key.rotated_at && <Badge variant="secondary">Rotated</Badge>}
                                </div>
                                <p className="mt-1 text-xs text-muted-foreground">
                                  Last used: {api_key.last_used_at ? new Date(api_key.last_used_at).toLocaleString() : 'Never'}
                                </p>
                              </div>
                              {can_manage && (
                                <div className="flex items-center gap-2">
                                  <Button variant="outline" size="sm" onClick={() => { set_api_action({ type: 'rotate', project_id: project.project_id, key_id: api_key.key_id }); set_api_key_confirmation('') }}>
                                    <RefreshCcw className="h-4 w-4" />
                                    Rotate
                                  </Button>
                                  <Button variant="destructive" size="sm" onClick={() => { set_api_action({ type: 'revoke', project_id: project.project_id, key_id: api_key.key_id }); set_api_key_confirmation('') }}>
                                    Revoke
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
            })
          )}
        </CardContent>
      </Card>

      <Dialog open={dialog_mode !== null} onOpenChange={(open) => !open && set_dialog_mode(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {dialog_mode === 'create' && 'Create project'}
              {dialog_mode === 'rename' && 'Rename project'}
              {dialog_mode === 'delete' && 'Delete project'}
            </DialogTitle>
            <DialogDescription>
              {dialog_mode === 'delete'
                ? `Type ${active_project?.name ?? 'the project name'} to confirm deletion.`
                : 'Project names must follow the server validation rules.'}
            </DialogDescription>
          </DialogHeader>

          {(dialog_mode === 'create' || dialog_mode === 'rename') && (
            <div className="space-y-2">
              <Label htmlFor="project_name">Project name</Label>
              <Input id="project_name" value={name} onChange={(e) => set_name(e.target.value)} />
            </div>
          )}

          {dialog_mode === 'delete' && active_project && (
            <div className="space-y-2">
              <Label htmlFor="project_confirm">Type {active_project.name} to confirm</Label>
              <Input id="project_confirm" value={name} onChange={(e) => set_name(e.target.value)} />
            </div>
          )}

          <ErrorAlert message={error} />

          <DialogFooter>
            <Button variant="outline" onClick={() => set_dialog_mode(null)}>Cancel</Button>
            <Button
              variant={dialog_mode === 'delete' ? 'destructive' : 'default'}
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
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{api_action?.type === 'rotate' ? 'Rotate API key' : 'Revoke API key'}</DialogTitle>
            <DialogDescription>
              {api_action?.type === 'rotate' ? 'Type ROTATE to confirm. A new raw key will be shown once.' : 'Type REVOKE to confirm.'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="api_confirmation">Confirmation</Label>
            <Input id="api_confirmation" value={api_key_confirmation} onChange={(e) => set_api_key_confirmation(e.target.value)} />
          </div>
          <ErrorAlert message={error} />
          <DialogFooter>
            <Button variant="outline" onClick={() => set_api_action(null)}>Cancel</Button>
            <Button
              variant={api_action?.type === 'revoke' ? 'destructive' : 'default'}
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
              Confirm
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={raw_key !== null} onOpenChange={(open) => !open && set_raw_key(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Raw API key</DialogTitle>
            <DialogDescription>This is the only time the raw key will be shown. Store it securely.</DialogDescription>
          </DialogHeader>
          <div className="rounded-md border bg-muted/50 p-4 font-mono text-sm break-all">{raw_key}</div>
          <DialogFooter>
            <Button onClick={() => set_raw_key(null)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ErrorAlert message={error} />
    </div>
  )
}
