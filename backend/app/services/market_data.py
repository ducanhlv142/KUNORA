from collections.abc import Sequence

from app.domain.market import (
    Candle,
    CandleInterval,
    Instrument,
    MarketDataProvider,
    Quote,
)


class MarketDataService:
    def __init__(
        self,
        provider: MarketDataProvider,
    ) -> None:
        self._provider = provider

    async def get_instruments(self) -> Sequence[Instrument]:
        return await self._provider.get_instruments()

    async def get_instrument(
        self,
        instrument_id: str,
    ) -> Instrument:
        return await self._provider.get_instrument(
            instrument_id
        )


    async def get_quote(
        self,
        instrument_id: str,
    ) -> Quote:
        return await self._provider.get_quote(
            instrument_id
        )

    async def get_candles(
        self,
        instrument_id: str,
        interval: CandleInterval,
        limit: int = 500,
    ) -> Sequence[Candle]:
        if not 1 <= limit <= 1000:
            raise ValueError(
                "limit must be between 1 and 1000"
            )

        return await self._provider.get_candles(
            instrument_id,
            interval,
            limit,
        )