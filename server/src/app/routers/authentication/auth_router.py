from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import ORJSONResponse

from server.src.app.routers.authentication.cookie_policy import remove_session_cookie, set_device_cookie, set_session_cookie
from server.src.app.routers.classes.authentication_classes import AuthenticatedUserResponse, CompleteDeletionRequest, CompleteEmailChangeRequest, CompleteLoginRequest, CompleteLogoutRequest, CompletePasswordChangeRequest, CompletePasswordResetRequest, CompleteSignupRequest, DeleteDevicesRequest, EmailHashResponse, InitiateDeletionRequest, InitiateEmailChangeRequest, InitiateLoginRequest, InitiatePasswordResetRequest, InitiateSignupRequest, MobileAuthResponse, OAuthCallbackRequest, OAuthInitiateResponse, ResendOtpAuthenticatedRequest, ResendOtpPublicRequest, ResetTokenResponse, SessionResponse, UserDeviceItem, UserDevicesResponse, UserIdResponse, UserProfileResponse, UserSessionItem, UserSessionsResponse, VerifyPasswordResetRequest
from server.src.app.routers.classes.base import BaseResponse
from server.src.app.routers.dependencies.router_dependencies import CountryDep, DeviceDep, DeviceTokenDep, EventPublisherDep, HTTPDep, LuaManagerDep, OsDep, PoolDep, RedisDep, SessionTokenDep, UserDep
from server.src.logic.authentication.deletion.complete_deletion import complete_deletion
from server.src.logic.authentication.deletion.initiate_deletion import initiate_deletion
from server.src.logic.authentication.device.complete_deletion import delete_devices
from server.src.logic.authentication.email.complete_email_change import complete_email_change
from server.src.logic.authentication.email.initiate_email_change import initiate_email_change
from server.src.logic.authentication.login.complete_login import complete_login
from server.src.logic.authentication.login.initiate_login import initiate_login
from server.src.logic.authentication.login.oauth.github.complete_github_oauth import complete_github_oauth
from server.src.logic.authentication.login.oauth.github.initiate_github_oauth import initiate_github_oauth_logic
from server.src.logic.authentication.login.oauth.google.complete_google_oauth import complete_google_oauth
from server.src.logic.authentication.login.oauth.google.initiate_google_oauth import initiate_google_oauth_logic
from server.src.logic.authentication.logout.logout import logout
from server.src.logic.authentication.password.change.complete_change import complete_password_change
from server.src.logic.authentication.password.reset.complete_reset import complete_password_reset
from server.src.logic.authentication.password.reset.initiate_reset import initiate_password_reset
from server.src.logic.authentication.password.reset.verify_reset_otp import verify_password_reset_otp
from server.src.logic.authentication.resend.resend_otp_authenticated import resend_otp_authenticated
from server.src.logic.authentication.resend.resend_otp_public import resend_otp_public
from server.src.logic.authentication.shared.resolve_current_user import resolve_current_user
from server.src.logic.authentication.shared.ui.get_auth_functions import get_user_devices_data, get_user_profile_data, get_user_sessions_data
from server.src.logic.authentication.signup.complete_signup import complete_signup
from server.src.logic.authentication.signup.initiate_signup import initiate_signup

router = APIRouter(prefix="/v1", default_response_class=ORJSONResponse)

# --- Signup ---

@router.post("/auth/signup/initiate", response_model=EmailHashResponse)
async def signup_initiate(body: InitiateSignupRequest, cache: RedisDep, pool: PoolDep, country: CountryDep, device: DeviceDep):
    result = await initiate_signup(pool, cache, body.email, body.password, country, device, body.name)
    return EmailHashResponse(email_hash=result.email_hash)

@router.post("/auth/signup/complete", response_model=SessionResponse | MobileAuthResponse)
async def signup_complete(
    response: Response,
    body: CompleteSignupRequest,
    cache: RedisDep,
    lua_manager: LuaManagerDep,
    pool: PoolDep,
    country: CountryDep,
    device: DeviceDep,
    publisher: EventPublisherDep,
    os: OsDep,
):
    result = await complete_signup(pool, cache, lua_manager, body.email_hash, body.otp, country, device, publisher)

    if os == "web":
        set_session_cookie(response, result.session_token, result.expires_at)
        set_device_cookie(response, result.device_token)
        return SessionResponse(expires_at=result.expires_at)

    return MobileAuthResponse(session_token=result.session_token, device_token=result.device_token, expires_at=result.expires_at)

# --- Login ---

@router.post("/auth/login/initiate", response_model=EmailHashResponse | SessionResponse | MobileAuthResponse)
async def login_initiate(
    response: Response,
    body: InitiateLoginRequest,
    cache: RedisDep,
    lua_manager: LuaManagerDep,
    pool: PoolDep,
    country: CountryDep,
    device: DeviceDep,
    device_token: DeviceTokenDep,
    publisher: EventPublisherDep,
    os: OsDep,
):
    result = await initiate_login(pool, cache, lua_manager, body.email, body.password, country, device, publisher, device_token)

    if result.session_token:
        if os == "web":
            set_session_cookie(response, result.session_token, result.expires_at)
            return SessionResponse(expires_at=result.expires_at)
        return MobileAuthResponse(session_token=result.session_token, device_token=None, expires_at=result.expires_at)

    if os == "web" and result.clear_device_cookie:
        response.delete_cookie(key="X-Device-Token", path="/")

    return EmailHashResponse(email_hash=result.email_hash)

@router.post("/auth/login/complete", response_model=SessionResponse | MobileAuthResponse)
async def login_complete(
    response: Response,
    body: CompleteLoginRequest,
    cache: RedisDep,
    lua_manager: LuaManagerDep,
    pool: PoolDep,
    country: CountryDep,
    device: DeviceDep,
    publisher: EventPublisherDep,
    os: OsDep,
):
    result = await complete_login(pool, cache, lua_manager, body.email_hash, body.otp, country, device, publisher)

    if os == "web":
        set_session_cookie(response, result.session_token, result.expires_at)
        set_device_cookie(response, result.device_token)
        return SessionResponse(expires_at=result.expires_at)

    return MobileAuthResponse(session_token=result.session_token, device_token=result.device_token, expires_at=result.expires_at)

# --- Email Change ---

@router.post("/auth/email/change/initiate", response_model=UserIdResponse)
async def email_change_initiate(body: InitiateEmailChangeRequest, cache: RedisDep, lua_manager: LuaManagerDep, pool: PoolDep, user_id: UserDep, country: CountryDep, device: DeviceDep):
    result = await initiate_email_change(pool, cache, lua_manager, user_id, body.new_email, country, device)
    return UserIdResponse(user_id=result.user_id)

@router.post("/auth/email/change/complete", response_model=BaseResponse)
async def email_change_complete(body: CompleteEmailChangeRequest, cache: RedisDep, pool: PoolDep, user_id: UserDep, country: CountryDep, device: DeviceDep):
    await complete_email_change(pool, cache, user_id, body.otp, country, device)
    return BaseResponse()

# --- Account Deletion ---

@router.post("/auth/account/delete/initiate", response_model=UserIdResponse)
async def deletion_initiate(body: InitiateDeletionRequest, cache: RedisDep, lua_manager: LuaManagerDep, pool: PoolDep, user_id: UserDep, country: CountryDep, device: DeviceDep):
    result = await initiate_deletion(pool, cache, lua_manager, user_id, country, device)
    return UserIdResponse(user_id=result.user_id)

@router.post("/auth/account/delete/complete", response_model=BaseResponse)
async def deletion_complete(body: CompleteDeletionRequest, cache: RedisDep, lua_manager: LuaManagerDep, pool: PoolDep, user_id: UserDep, country: CountryDep, device: DeviceDep, publisher: EventPublisherDep):
    await complete_deletion(pool, cache, lua_manager, user_id, body.otp, country, device, publisher)
    return BaseResponse()

# --- User Resolution ---

@router.get("/auth/user/me", response_model=AuthenticatedUserResponse)
async def get_current_user_endpoint(
    pool: PoolDep,
    session_token: SessionTokenDep,
):
    user = await resolve_current_user(pool, session_token)
    if user is None:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return AuthenticatedUserResponse(user=user)

@router.get("/auth/user/profile", response_model=UserProfileResponse)
async def get_user_profile_endpoint(pool: PoolDep, user_id: UserDep):
    profile = await get_user_profile_data(pool, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    return UserProfileResponse(
        user_id=profile.user_id,
        email=profile.email,
        name=profile.name,
        account_plan=profile.account_plan,
        account_status=profile.account_status,
        provider=profile.provider,
        avatar_url=profile.avatar_url,
        created_at=profile.created_at,
    )

@router.get("/auth/user/sessions", response_model=UserSessionsResponse)
async def get_user_sessions_endpoint(pool: PoolDep, user_id: UserDep):
    sessions = await get_user_sessions_data(pool, user_id)
    return UserSessionsResponse(
        sessions=[
            UserSessionItem(session_id=s.session_id, device_id=s.device_id, country=s.country, device=s.device, created_at=s.created_at, expires_at=s.expires_at)
            for s in sessions
        ]
    )

@router.get("/auth/user/devices", response_model=UserDevicesResponse)
async def get_user_devices_endpoint(pool: PoolDep, user_id: UserDep):
    devices = await get_user_devices_data(pool, user_id)
    return UserDevicesResponse(
        devices=[
            UserDeviceItem(device_id=d.device_id, device_name=d.device_name, created_at=d.created_at, expires_at=d.expires_at)
            for d in devices
        ]
    )

# --- Logout ---

@router.post("/auth/logout", response_model=BaseResponse)
async def logout_complete(
    response: Response,
    body: CompleteLogoutRequest,
    pool: PoolDep,
    cache: RedisDep,
    lua_manager: LuaManagerDep,
    session_token: SessionTokenDep,
    publisher: EventPublisherDep,
    os: OsDep,
):
    await logout(pool, cache, lua_manager, session_token, publisher)
    if os == "web":
        remove_session_cookie(response)
    return BaseResponse()

# --- Password Management ---

@router.post("/auth/password/change/complete", response_model=BaseResponse)
async def password_change_complete(body: CompletePasswordChangeRequest, cache: RedisDep, lua_manager: LuaManagerDep, pool: PoolDep, user_id: UserDep, country: CountryDep, device: DeviceDep, session_token: SessionTokenDep, publisher: EventPublisherDep):
    await complete_password_change(pool, cache, lua_manager, user_id, body.old_password, body.new_password, country, device, session_token, publisher)
    return BaseResponse()

@router.post("/auth/password/reset/initiate", response_model=BaseResponse)
async def password_reset_initiate(body: InitiatePasswordResetRequest, cache: RedisDep, pool: PoolDep, country: CountryDep, device: DeviceDep):
    await initiate_password_reset(pool, cache, body.email, country, device)
    return BaseResponse()

@router.post("/auth/password/reset/verify", response_model=ResetTokenResponse)
async def password_reset_verify(body: VerifyPasswordResetRequest, cache: RedisDep):
    reset_token = await verify_password_reset_otp(cache, body.email, body.otp)
    return ResetTokenResponse(reset_token=reset_token)

@router.post("/auth/password/reset/complete", response_model=BaseResponse)
async def password_reset_complete(body: CompletePasswordResetRequest, cache: RedisDep, lua_manager: LuaManagerDep, pool: PoolDep, country: CountryDep, device: DeviceDep, publisher: EventPublisherDep):
    await complete_password_reset(pool, cache, lua_manager, body.reset_token, body.new_password, country, device, publisher)
    return BaseResponse()

# --- Device Management ---

@router.post("/auth/devices/delete", response_model=BaseResponse)
async def devices_delete(
    body: DeleteDevicesRequest,
    pool: PoolDep,
    cache: RedisDep,
    lua_manager: LuaManagerDep,
    user_id: UserDep,
    publisher: EventPublisherDep,
):
    await delete_devices(pool, cache, lua_manager, user_id, body.device_ids, publisher)
    return BaseResponse()

# --- OTP Resend ---

@router.post("/auth/otp/resend", response_model=BaseResponse)
async def otp_resend_public(
    body: ResendOtpPublicRequest,
    cache: RedisDep,
    lua_manager: LuaManagerDep,
    pool: PoolDep,
    country: CountryDep,
    device: DeviceDep,
):
    await resend_otp_public(cache, lua_manager, pool, body.email, body.email_hash, country, device)
    return BaseResponse()

@router.post("/auth/otp/resend/authenticated", response_model=BaseResponse)
async def otp_resend_authenticated(
    body: ResendOtpAuthenticatedRequest,
    cache: RedisDep,
    lua_manager: LuaManagerDep,
    pool: PoolDep,
    user_id: UserDep,
    country: CountryDep,
    device: DeviceDep,
):
    await resend_otp_authenticated(cache, lua_manager, pool, user_id, country, device)
    return BaseResponse()

# --- OAuth ---

@router.get("/auth/oauth/google/initiate", response_model=OAuthInitiateResponse)
async def google_oauth_initiate(cache: RedisDep):
    result = await initiate_google_oauth_logic(cache)
    return OAuthInitiateResponse(redirect_url=result.redirect_url)

@router.post("/auth/oauth/google/callback", response_model=SessionResponse | MobileAuthResponse)
async def google_oauth_callback(
    response: Response,
    body: OAuthCallbackRequest,
    pool: PoolDep,
    cache: RedisDep,
    lua_manager: LuaManagerDep,
    http: HTTPDep,
    country: CountryDep,
    device: DeviceDep,
    publisher: EventPublisherDep,
    os: OsDep,
):
    result = await complete_google_oauth(pool, cache, lua_manager, http, body.code, body.state, country, device, publisher)
    if os == "web":
        set_session_cookie(response, result.session_token, result.expires_at)
        if result.device_token:
            set_device_cookie(response, result.device_token)
        return SessionResponse(expires_at=result.expires_at)
    return MobileAuthResponse(session_token=result.session_token, device_token=result.device_token, expires_at=result.expires_at)

@router.get("/auth/oauth/github/initiate", response_model=OAuthInitiateResponse)
async def github_oauth_initiate(cache: RedisDep):
    result = await initiate_github_oauth_logic(cache)
    return OAuthInitiateResponse(redirect_url=result.redirect_url)

@router.post("/auth/oauth/github/callback", response_model=SessionResponse | MobileAuthResponse)
async def github_oauth_callback(
    response: Response,
    body: OAuthCallbackRequest,
    pool: PoolDep,
    cache: RedisDep,
    lua_manager: LuaManagerDep,
    http: HTTPDep,
    country: CountryDep,
    device: DeviceDep,
    publisher: EventPublisherDep,
    os: OsDep,
):
    result = await complete_github_oauth(pool, cache, lua_manager, http, body.code, body.state, country, device, publisher)
    if os == "web":
        set_session_cookie(response, result.session_token, result.expires_at)
        if result.device_token:
            set_device_cookie(response, result.device_token)
        return SessionResponse(expires_at=result.expires_at)
    return MobileAuthResponse(session_token=result.session_token, device_token=result.device_token, expires_at=result.expires_at)
