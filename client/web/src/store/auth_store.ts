import { create } from 'zustand'
import type { AuthStoreState } from '@/types/store_types'

export const use_auth_store = create<AuthStoreState>((set) => ({
  user: null,
  is_authenticated: false,
  is_loading: true,
  set_user: (user) => set({ user, is_authenticated: user !== null }),
  set_loading: (is_loading) => set({ is_loading }),
  clear: () => set({ user: null, is_authenticated: false, is_loading: false }),
}))
