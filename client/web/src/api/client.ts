import { BASE_URL } from '@/lib/constants'
import { use_auth_store } from '@/store/auth_store'
import { use_core_store } from '@/store/core_store'
import { use_dashboard_store } from '@/store/dashboard_store'
import type { ApiError } from '@/types/api_types'

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  body?: Record<string, unknown>
  idempotency_key?: string
}

export class ApiRequestError extends Error {
  code: string

  constructor(error: ApiError) {
    super(error.message)
    this.code = error.code
    this.name = 'ApiRequestError'
  }
}

let session_expired_handled = false

function handle_session_expired(): never {
  if (!session_expired_handled && use_auth_store.getState().is_authenticated) {
    session_expired_handled = true

    use_auth_store.getState().clear()
    const ds = use_dashboard_store.getState()
    ds.set_profile(null)
    ds.set_sessions([])
    ds.set_devices([])
    use_core_store.getState().clear()

    window.dispatchEvent(new Event('session-expired'))
  }

  throw new ApiRequestError({ code: 'SESSION_EXPIRED', message: 'Your session has expired.' })
}

export async function api_request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, idempotency_key } = options

  const headers: Record<string, string> = {
    'X-Client-Type': 'web',
  }

  if (body) {
    headers['Content-Type'] = 'application/json'
  }

  if (idempotency_key) {
    headers['X-Idempotency-Key'] = idempotency_key
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    credentials: 'include',
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (response.status === 401) {
    handle_session_expired()
  }

  const data = await response.json()

  if (!response.ok) {
    if (data?.error?.code) {
      throw new ApiRequestError(data.error)
    }
    if (data?.detail) {
      throw new ApiRequestError({ code: data.detail, message: data.detail })
    }
    throw new ApiRequestError({ code: 'UNKNOWN_ERROR', message: 'An unexpected error occurred.' })
  }

  return data as T
}
