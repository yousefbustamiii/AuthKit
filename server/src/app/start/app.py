from fastapi import FastAPI

from server.src.app.errors.base import AppError
from server.src.app.errors.handler import app_error_handler
from server.src.app.routers.authentication.auth_router import router as auth_router
from server.src.app.routers.core.core_router import router as core_router
from server.src.app.routers.core.stripe_webhooks import router as stripe_webhook_router
from server.src.app.routers.health import router as health_router
from server.src.app.start.context import lifespan
from server.src.app.start.middleware import setup_middleware

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    
    setup_middleware(app)
    
    app.add_exception_handler(AppError, app_error_handler)
    
    app.include_router(auth_router)
    app.include_router(core_router)
    app.include_router(stripe_webhook_router)
    app.include_router(health_router)
    
    return app
