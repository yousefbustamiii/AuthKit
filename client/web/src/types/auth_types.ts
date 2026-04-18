export type OtpContext = 'signup' | 'login' | 'email_change' | 'account_delete'

export interface OtpRouterState {
  context: OtpContext
  email_hash?: string
  email?: string
}

export interface PasswordResetVerifyState {
  email: string
}

export interface PasswordResetCompleteState {
  reset_token: string
}

export type LoginInitiateResult =
  | { needs_otp: true; email_hash: string }
  | { needs_otp: false }
