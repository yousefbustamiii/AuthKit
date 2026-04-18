from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from server.src.app.routers.classes.base import BaseResponse

# --- Request Classes ---

class DeleteDevicesRequest(BaseModel):
    device_ids: list[UUID] = Field(..., min_length=1, max_length=50)


class CompleteDeletionRequest(BaseModel):
    otp: str

class CompleteLoginRequest(BaseModel):
    email_hash: str
    otp: str

class CompleteLogoutRequest(BaseModel):
    pass

class CompleteEmailChangeRequest(BaseModel):
    otp: str

class CompletePasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class CompletePasswordResetRequest(BaseModel):
    reset_token: str
    new_password: str

class VerifyPasswordResetRequest(BaseModel):
    email: str
    otp: str

class InitiateDeletionRequest(BaseModel):
    pass

class InitiateLoginRequest(BaseModel):
    email: str
    password: str

class InitiateEmailChangeRequest(BaseModel):
    new_email: str

class InitiatePasswordResetRequest(BaseModel):
    email: str

class InitiateSignupRequest(BaseModel):
    email: str
    password: str
    name: str | None = None

class CompleteSignupRequest(BaseModel):
    email_hash: str
    otp: str

class ResendOtpPublicRequest(BaseModel):
    email: str
    email_hash: str

class ResendOtpAuthenticatedRequest(BaseModel):
    pass

# --- OAuth Request / Response Classes ---

class OAuthCallbackRequest(BaseModel):
    code: str
    state: str

# --- Response Classes ---

class EmailHashResponse(BaseResponse):
    email_hash: str

class AuthenticatedUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session_id: UUID
    user_id: UUID
    email: str
    account_status: str
    expires_at: datetime

class AuthenticatedUserResponse(BaseResponse):
    user: AuthenticatedUser | None

class SessionResponse(BaseResponse):
    expires_at: datetime

class MobileAuthResponse(BaseResponse):
    session_token: str
    device_token: str | None
    expires_at: datetime

class UserIdResponse(BaseResponse):
    user_id: UUID

class ResetTokenResponse(BaseResponse):
    reset_token: str

class OAuthInitiateResponse(BaseResponse):
    redirect_url: str


# --- User Data Response Classes ---

class UserProfileResponse(BaseResponse):
    user_id: UUID
    email: str
    name: str | None
    account_plan: str
    account_status: str
    provider: str
    avatar_url: str | None
    created_at: datetime


class UserSessionItem(BaseModel):
    session_id: UUID
    device_id: UUID | None
    country: str
    device: str
    created_at: datetime
    expires_at: datetime


class UserSessionsResponse(BaseResponse):
    sessions: list[UserSessionItem]


class UserDeviceItem(BaseModel):
    device_id: UUID
    device_name: str | None
    created_at: datetime
    expires_at: datetime | None


class UserDevicesResponse(BaseResponse):
    devices: list[UserDeviceItem]
