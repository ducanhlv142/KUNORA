from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.router import api_router
from app.providers.binance.provider import (
    BinanceMarketDataProvider,
)
from app.services.market_data import MarketDataService

@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    provider = BinanceMarketDataProvider()

    app.state.market_data_service = MarketDataService(
        provider
    )

    try:
        yield
    finally:
        await provider.close()


app = FastAPI(
    title="KUNORA API",
    description="Market Intelligence Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "KUNORA API",
        "version": "0.1.0",
        "status": "online",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }