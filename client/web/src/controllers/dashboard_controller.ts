import * as auth_api from '@/api/auth_api'
import { generate_idempotency_key } from '@/lib/idempotency'
import { use_auth_store } from '@/store/auth_store'
import { use_core_store } from '@/store/core_store'
import { use_dashboard_store } from '@/store/dashboard_store'
import { check_session } from '@/controllers/auth_controller'

export async function load_profile(): Promise<void> {
  const result = await auth_api.get_profile()
  use_dashboard_store.getState().set_profile(result)
}

export async function load_sessions(): Promise<void> {
  const result = await auth_api.get_sessions()
  use_dashboard_store.getState().set_sessions(result.sessions)
}

export async function load_devices(): Promise<void> {
  const result = await auth_api.get_devices()
  use_dashboard_store.getState().set_devices(result.devices)
}

export async function handle_delete_devices(device_ids: string[]): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.delete_devices({ device_ids }, key)
  await load_devices()
}

export async function handle_email_change_initiate(new_email: string): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.email_change_initiate({ new_email }, key)
}

export async function handle_email_change_complete(otp: string): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.email_change_complete({ otp }, key)
  await check_session()
}

export async function handle_password_change(
  old_password: string,
  new_password: string,
): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.password_change({ old_password, new_password }, key)
}

export async function handle_account_delete_initiate(): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.account_delete_initiate(key)
}

export async function handle_account_delete_complete(otp: string): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.account_delete_complete({ otp }, key)
  use_auth_store.getState().clear()
  const ds = use_dashboard_store.getState()
  ds.set_profile(null)
  ds.set_sessions([])
  ds.set_devices([])
  use_core_store.getState().clear()
}
