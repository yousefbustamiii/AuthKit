import * as auth_api from '@/api/auth_api'
import { generate_idempotency_key } from '@/lib/idempotency'
import { use_auth_store } from '@/store/auth_store'
import { use_core_store } from '@/store/core_store'
import { use_dashboard_store } from '@/store/dashboard_store'
import type { LoginInitiateResult } from '@/types/auth_types'

export async function check_session(): Promise<boolean> {
  const store = use_auth_store.getState()
  try {
    const result = await auth_api.get_me()
    if (result.user) {
      store.set_user(result.user)
      store.set_loading(false)
      return true
    }
    store.clear()
    return false
  } catch {
    store.clear()
    return false
  }
}

export async function handle_signup_initiate(
  email: string,
  password: string,
): Promise<{ email_hash: string }> {
  const key = generate_idempotency_key()
  const result = await auth_api.signup_initiate({ email, password }, key)
  return { email_hash: result.email_hash }
}

export async function handle_signup_complete(
  email_hash: string,
  otp: string,
): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.signup_complete({ email_hash, otp }, key)
  await check_session()
}

export async function handle_login_initiate(
  email: string,
  password: string,
): Promise<LoginInitiateResult> {
  const key = generate_idempotency_key()
  const result = await auth_api.login_initiate({ email, password }, key)

  if ('email_hash' in result) {
    return { needs_otp: true, email_hash: result.email_hash }
  }

  await check_session()
  return { needs_otp: false }
}

export async function handle_login_complete(
  email_hash: string,
  otp: string,
): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.login_complete({ email_hash, otp }, key)
  await check_session()
}

export async function handle_logout(): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.logout(key)
  use_auth_store.getState().clear()
  const ds = use_dashboard_store.getState()
  ds.set_profile(null)
  ds.set_sessions([])
  ds.set_devices([])
  use_core_store.getState().clear()
}

export async function handle_password_reset_initiate(email: string): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.password_reset_initiate({ email }, key)
}

export async function handle_password_reset_verify(
  email: string,
  otp: string,
): Promise<{ reset_token: string }> {
  const result = await auth_api.password_reset_verify({ email, otp })
  return { reset_token: result.reset_token }
}

export async function handle_password_reset_complete(
  reset_token: string,
  new_password: string,
): Promise<void> {
  const key = generate_idempotency_key()
  await auth_api.password_reset_complete({ reset_token, new_password }, key)
}

export async function handle_resend_otp_public(
  email: string,
  email_hash: string,
): Promise<void> {
  await auth_api.otp_resend_public({ email, email_hash })
}

export async function handle_resend_otp_authenticated(): Promise<void> {
  await auth_api.otp_resend_authenticated()
}

export async function handle_google_oauth_initiate(): Promise<string> {
  const result = await auth_api.oauth_google_initiate()
  return result.redirect_url
}

export async function handle_github_oauth_initiate(): Promise<string> {
  const result = await auth_api.oauth_github_initiate()
  return result.redirect_url
}

export async function handle_google_oauth_callback(code: string, state: string): Promise<void> {
  await auth_api.oauth_google_callback({ code, state })
  await check_session()
}

export async function handle_github_oauth_callback(code: string, state: string): Promise<void> {
  await auth_api.oauth_github_callback({ code, state })
  await check_session()
}
