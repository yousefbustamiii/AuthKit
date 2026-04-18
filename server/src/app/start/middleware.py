from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from server.src.app.config.cloudflare_ip_ranges import is_cloudflare_ip
from server.src.app.config.settings import settings
from server.src.app.middleware.middleware_chain import MiddlewareChain

async def cloudflare_only_guard(request: Request, call_next):
    if not settings.cf_guard_enabled:
        return await call_next(request)

    remote_addr = request.client.host if request.client else None

    cf_ranges = request.app.state.cf_ip_ranges
    if remote_addr is None or not is_cloudflare_ip(remote_addr, cf_ranges):
        return JSONResponse(status_code=403, content={"detail": "DIRECT_ACCESS_FORBIDDEN"})

    return await call_next(request)

def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(MiddlewareChain)
    app.middleware("http")(cloudflare_only_guard)