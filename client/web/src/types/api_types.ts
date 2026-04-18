// --- Base ---

export interface ApiError {
  code: string
  message: string
}

export interface BaseResponse {
  success: boolean
  error?: ApiError
}

// --- Auth Responses ---

export interface EmailHashResponse extends BaseResponse {
  email_hash: string
}

export interface SessionResponse extends BaseResponse {
  expires_at: string
}

export interface UserIdResponse extends BaseResponse {
  user_id: string
}

export interface ResetTokenResponse extends BaseResponse {
  reset_token: string
}

export interface OAuthInitiateResponse extends BaseResponse {
  redirect_url: string
}

// --- User Data ---

export interface AuthenticatedUser {
  session_id: string
  user_id: string
  email: string
  account_status: string
  expires_at: string
}

export interface AuthenticatedUserResponse extends BaseResponse {
  user: AuthenticatedUser | null
}

export interface UserProfileResponse extends BaseResponse {
  user_id: string
  email: string
  name: string | null
  account_plan: string
  account_status: string
  provider: string
  avatar_url: string | null
  created_at: string
}

export interface UserSessionItem {
  session_id: string
  device_id: string | null
  country: string
  device: string
  created_at: string
  expires_at: string
}

export interface UserSessionsResponse extends BaseResponse {
  sessions: UserSessionItem[]
}

export interface UserDeviceItem {
  device_id: string
  device_name: string | null
  created_at: string
  expires_at: string | null
}

export interface UserDevicesResponse extends BaseResponse {
  devices: UserDeviceItem[]
}

// --- Request Bodies ---

export interface SignupInitiateRequest {
  email: string
  password: string
}

export interface SignupCompleteRequest {
  email_hash: string
  otp: string
}

export interface LoginInitiateRequest {
  email: string
  password: string
}

export interface LoginCompleteRequest {
  email_hash: string
  otp: string
}

export interface PasswordResetInitiateRequest {
  email: string
}

export interface PasswordResetVerifyRequest {
  email: string
  otp: string
}

export interface PasswordResetCompleteRequest {
  reset_token: string
  new_password: string
}

export interface PasswordChangeRequest {
  old_password: string
  new_password: string
}

export interface EmailChangeInitiateRequest {
  new_email: string
}

export interface EmailChangeCompleteRequest {
  otp: string
}

export interface DeleteAccountCompleteRequest {
  otp: string
}

export interface DeleteDevicesRequest {
  device_ids: string[]
}

export interface ResendOtpPublicRequest {
  email: string
  email_hash: string
}

export interface OAuthCallbackRequest {
  code: string
  state: string
}
