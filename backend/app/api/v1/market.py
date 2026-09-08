from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_market_data_service
from app.domain.market import (
    Candle,
    CandleInterval,
    Instrument,
    Quote,
)
from app.services.market_data import MarketDataService


router = APIRouter(
    prefix="/market",
    tags=["market"],
)

MarketService = Annotated[
    MarketDataService,
    Depends(get_market_data_service),
]


@router.get(
    "/instruments/{instrument_id}",
    response_model=Instrument,
)
async def get_instrument(
    instrument_id: str,
    service: MarketService,
) -> Instrument:
    return await service.get_instrument(
        instrument_id
    )


@router.get(
    "/quotes/{instrument_id}",
    response_model=Quote,
)
async def get_quote(
    instrument_id: str,
    service: MarketService,
) -> Quote:
    return await service.get_quote(
        instrument_id
    )


@router.get(
    "/candles/{instrument_id}",
    response_model=list[Candle],
)
async def get_candles(
    instrument_id: str,
    service: MarketService,
    interval: CandleInterval = CandleInterval.ONE_HOUR,
    limit: int = Query(
        default=500,
        ge=1,
        le=1000,
    ),
) -> list[Candle]:
    candles = await service.get_candles(
        instrument_id,
        interval,
        limit,
    )

    return list(candles)