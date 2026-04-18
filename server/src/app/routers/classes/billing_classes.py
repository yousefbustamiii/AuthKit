from pydantic import BaseModel

from server.src.app.routers.classes.base import BaseResponse

class CreateCheckoutSessionRequest(BaseModel):
    plan_number: int


class CreateCheckoutSessionResponse(BaseResponse):
    checkout_url: str


class UpgradePlanRequest(BaseModel):
    plan_number: int
