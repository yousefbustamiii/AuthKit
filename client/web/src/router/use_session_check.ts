import { useEffect, useRef } from 'react'
import { check_session } from '@/controllers/auth_controller'
import { use_auth_store } from '@/store/auth_store'

export function useSessionCheck() {
  const is_loading = use_auth_store((s) => s.is_loading)
  const is_checking = useRef(false)

  useEffect(() => {
    if (is_loading && !is_checking.current) {
      is_checking.current = true
      check_session().finally(() => {
        is_checking.current = false
      })
    }
  }, [is_loading])
}
