from server.src.app.errors.base import AppError

# -- Shared --

class OtpVerificationError(AppError):
    code = "INVALID_OTP"
    status_code = 400
    message = "Invalid or expired OTP."

# -- Signup --

class EmailAlreadyTakenError(AppError):
    code = "EMAIL_ALREADY_TAKEN"
    status_code = 409
    message = "This email is already associated with an account."

class PendingSignupNotFoundError(AppError):
    code = "PENDING_SIGNUP_NOT_FOUND"
    status_code = 404
    message = "No pending signup found."

# -- Email --

class PendingEmailChangeNotFoundError(AppError):
    code = "PENDING_EMAIL_CHANGE_NOT_FOUND"
    status_code = 404
    message = "No pending email change found."

# -- Deletion --

class PendingUserDeletionNotFoundError(AppError):
    code = "PENDING_USER_DELETION_NOT_FOUND"
    status_code = 404
    message = "No pending deletion found."

# -- Password --

class IncorrectPasswordError(AppError):
    code = "INCORRECT_PASSWORD"
    status_code = 400
    message = "Incorrect password."

class SamePasswordError(AppError):
    code = "SAME_PASSWORD"
    status_code = 400
    message = "New password cannot be the same as the old password."

class InvalidEmailError(AppError):
    code = "INVALID_EMAIL"
    status_code = 400
    message = "The provided email is invalid."

    def __init__(self, detail: str = None):
        super().__init__()
        if detail:
            self.message = detail

class InvalidPasswordError(AppError):
    code = "INVALID_PASSWORD"
    status_code = 400
    message = "The provided password does not meet complexity requirements."

    def __init__(self, detail: str = None):
        super().__init__()
        if detail:
            self.message = detail

class UserNotFoundError(AppError):
    code = "USER_NOT_FOUND"
    status_code = 404
    message = "User not found."

# -- Resend OTP --

class NoPendingFlowError(AppError):
    code = "NO_PENDING_FLOW"
    status_code = 404
    message = "No active pending flow found for this identity."

# -- OAuth --

class OAuthStateMismatchError(AppError):
    code = "OAUTH_STATE_MISMATCH"
    status_code = 400
    message = "OAuth state token is invalid or expired. Please restart the login flow."

class OAuthProviderError(AppError):
    code = "OAUTH_PROVIDER_ERROR"
    status_code = 502
    message = "Failed to communicate with the OAuth provider. Please try again."

class OAuthEmailNotVerifiedError(AppError):
    code = "OAUTH_EMAIL_NOT_VERIFIED"
    status_code = 400
    message = "The email on this OAuth account is not verified. Please verify it with the provider first."

class OAuthProviderActionNotAllowedError(AppError):
    code = "OAUTH_PROVIDER_ACTION_NOT_ALLOWED"
    status_code = 403
    message = "This action is not available for accounts linked to an OAuth provider."