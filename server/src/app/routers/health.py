from fastapi import APIRouter

from server.src.app.routers.classes.base import BaseResponse

router = APIRouter(prefix="/v1")

@router.get("/health", response_model=BaseResponse)
async def health_check():
    return BaseResponse(success=True)
