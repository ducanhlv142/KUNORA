from fastapi import APIRouter

from app.api.v1.market import (
    router as market_router,
)
from app.api.ws.market import (
    router as market_ws_router,
)


api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(
    market_router
)

api_router.include_router(
    market_ws_router
)