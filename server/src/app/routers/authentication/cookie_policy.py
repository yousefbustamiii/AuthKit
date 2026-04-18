from fastapi import Response

from server.src.app.config.settings import settings

COOKIE_OPTS = dict(
    httponly=True,
    secure=settings.session.cookie_secure,
    samesite=settings.session.cookie_samesite,
    path="/",
)

DEVICE_COOKIE_OPTS = dict(
    **COOKIE_OPTS,
)

def set_session_cookie(response: Response, token: str, expires_at) -> None:
    response.set_cookie(
        key="X-Session-Token",
        value=token,
        expires=expires_at,
        max_age=settings.session.expire_days * 24 * 60 * 60,
        **COOKIE_OPTS,
    )

def set_device_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="X-Device-Token",
        value=token,
        **DEVICE_COOKIE_OPTS,
        max_age=365 * 24 * 60 * 60,  # 1 year, matches DB expires_at
    )

def remove_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key="X-Session-Token",
        path="/",
        secure=settings.session.cookie_secure,
        samesite=settings.session.cookie_samesite,
    )
