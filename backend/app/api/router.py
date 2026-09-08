from fastapi import APIRouter

from app.api.v1.market import router as market_router


api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(
    market_router
)