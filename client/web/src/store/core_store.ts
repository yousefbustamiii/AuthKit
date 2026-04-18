import { create } from 'zustand'
import type { CoreStoreState } from '@/types/store_types'

export const use_core_store = create<CoreStoreState>((set) => ({
  organizations: [],
  selected_organization_id: null,
  members_by_org: {},
  invitations_by_org: {},
  projects_by_org: {},
  api_keys_by_project: {},
  billing_by_org: {},
  set_organizations: (organizations) => set({ organizations }),
  set_selected_organization_id: (selected_organization_id) => set({ selected_organization_id }),
  set_members: (organization_id, members) =>
    set((state) => ({ members_by_org: { ...state.members_by_org, [organization_id]: members } })),
  set_invitations: (organization_id, invitations) =>
    set((state) => ({ invitations_by_org: { ...state.invitations_by_org, [organization_id]: invitations } })),
  set_projects: (organization_id, projects) =>
    set((state) => ({ projects_by_org: { ...state.projects_by_org, [organization_id]: projects } })),
  set_api_keys: (project_id, api_keys) =>
    set((state) => ({ api_keys_by_project: { ...state.api_keys_by_project, [project_id]: api_keys } })),
  set_billing: (organization_id, billing) =>
    set((state) => ({ billing_by_org: { ...state.billing_by_org, [organization_id]: billing } })),
  remove_organization: (organization_id) =>
    set((state) => {
      const projects = state.projects_by_org[organization_id] ?? []
      const members_by_org = { ...state.members_by_org }
      const invitations_by_org = { ...state.invitations_by_org }
      const projects_by_org = { ...state.projects_by_org }
      const billing_by_org = { ...state.billing_by_org }
      const api_keys_by_project = { ...state.api_keys_by_project }

      delete members_by_org[organization_id]
      delete invitations_by_org[organization_id]
      delete projects_by_org[organization_id]
      delete billing_by_org[organization_id]

      for (const project of projects) {
        delete api_keys_by_project[project.project_id]
      }

      return {
        organizations: state.organizations.filter((org) => org.organization_id !== organization_id),
        selected_organization_id:
          state.selected_organization_id === organization_id ? null : state.selected_organization_id,
        members_by_org,
        invitations_by_org,
        projects_by_org,
        api_keys_by_project,
        billing_by_org,
      }
    }),
  clear: () =>
    set({
      organizations: [],
      selected_organization_id: null,
      members_by_org: {},
      invitations_by_org: {},
      projects_by_org: {},
      api_keys_by_project: {},
      billing_by_org: {},
    }),
}))
