import { api_request } from './client'
import type {
  AuthenticatedUserResponse,
  BaseResponse,
  DeleteDevicesRequest,
  EmailChangeCompleteRequest,
  EmailChangeInitiateRequest,
  EmailHashResponse,
  LoginCompleteRequest,
  LoginInitiateRequest,
  OAuthCallbackRequest,
  OAuthInitiateResponse,
  PasswordChangeRequest,
  PasswordResetCompleteRequest,
  PasswordResetInitiateRequest,
  PasswordResetVerifyRequest,
  ResendOtpPublicRequest,
  ResetTokenResponse,
  SessionResponse,
  SignupCompleteRequest,
  SignupInitiateRequest,
  UserDevicesResponse,
  UserIdResponse,
  UserProfileResponse,
  UserSessionsResponse,
} from '@/types/api_types'

const AUTH = '/v1/auth'

export async function signup_initiate(
  body: SignupInitiateRequest,
  idempotency_key: string,
): Promise<EmailHashResponse> {
  return api_request<EmailHashResponse>(`${AUTH}/signup/initiate`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function signup_complete(
  body: SignupCompleteRequest,
  idempotency_key: string,
): Promise<SessionResponse> {
  return api_request<SessionResponse>(`${AUTH}/signup/complete`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function login_initiate(
  body: LoginInitiateRequest,
  idempotency_key: string,
): Promise<EmailHashResponse | SessionResponse> {
  return api_request<EmailHashResponse | SessionResponse>(`${AUTH}/login/initiate`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function login_complete(
  body: LoginCompleteRequest,
  idempotency_key: string,
): Promise<SessionResponse> {
  return api_request<SessionResponse>(`${AUTH}/login/complete`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function get_me(): Promise<AuthenticatedUserResponse> {
  return api_request<AuthenticatedUserResponse>(`${AUTH}/user/me`)
}

export async function get_profile(): Promise<UserProfileResponse> {
  return api_request<UserProfileResponse>(`${AUTH}/user/profile`)
}

export async function get_sessions(): Promise<UserSessionsResponse> {
  return api_request<UserSessionsResponse>(`${AUTH}/user/sessions`)
}

export async function get_devices(): Promise<UserDevicesResponse> {
  return api_request<UserDevicesResponse>(`${AUTH}/user/devices`)
}

export async function logout(idempotency_key: string): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${AUTH}/logout`, {
    method: 'POST',
    body: {},
    idempotency_key,
  })
}

export async function email_change_initiate(
  body: EmailChangeInitiateRequest,
  idempotency_key: string,
): Promise<UserIdResponse> {
  return api_request<UserIdResponse>(`${AUTH}/email/change/initiate`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function email_change_complete(
  body: EmailChangeCompleteRequest,
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${AUTH}/email/change/complete`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function account_delete_initiate(idempotency_key: string): Promise<UserIdResponse> {
  return api_request<UserIdResponse>(`${AUTH}/account/delete/initiate`, {
    method: 'POST',
    body: {},
    idempotency_key,
  })
}

export async function account_delete_complete(
  body: { otp: string },
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${AUTH}/account/delete/complete`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function password_change(
  body: PasswordChangeRequest,
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${AUTH}/password/change/complete`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function password_reset_initiate(
  body: PasswordResetInitiateRequest,
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${AUTH}/password/reset/initiate`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function password_reset_verify(
  body: PasswordResetVerifyRequest,
): Promise<ResetTokenResponse> {
  return api_request<ResetTokenResponse>(`${AUTH}/password/reset/verify`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
  })
}

export async function password_reset_complete(
  body: PasswordResetCompleteRequest,
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${AUTH}/password/reset/complete`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function otp_resend_public(
  body: ResendOtpPublicRequest,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${AUTH}/otp/resend`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
  })
}

export async function otp_resend_authenticated(): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${AUTH}/otp/resend/authenticated`, {
    method: 'POST',
    body: {},
  })
}

export async function delete_devices(
  body: DeleteDevicesRequest,
  idempotency_key: string,
): Promise<BaseResponse> {
  return api_request<BaseResponse>(`${AUTH}/devices/delete`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
    idempotency_key,
  })
}

export async function oauth_google_initiate(): Promise<OAuthInitiateResponse> {
  return api_request<OAuthInitiateResponse>(`${AUTH}/oauth/google/initiate`)
}

export async function oauth_github_initiate(): Promise<OAuthInitiateResponse> {
  return api_request<OAuthInitiateResponse>(`${AUTH}/oauth/github/initiate`)
}

export async function oauth_google_callback(
  body: OAuthCallbackRequest,
): Promise<SessionResponse> {
  return api_request<SessionResponse>(`${AUTH}/oauth/google/callback`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
  })
}

export async function oauth_github_callback(
  body: OAuthCallbackRequest,
): Promise<SessionResponse> {
  return api_request<SessionResponse>(`${AUTH}/oauth/github/callback`, {
    method: 'POST',
    body: body as unknown as Record<string, unknown>,
  })
}
