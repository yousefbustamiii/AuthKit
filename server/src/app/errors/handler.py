from fastapi import Request
from fastapi.responses import ORJSONResponse

from server.src.app.errors.base import AppError

async def app_error_handler(request: Request, exc: AppError):
    return ORJSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )