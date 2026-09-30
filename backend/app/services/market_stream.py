from collections.abc import (
    AsyncIterator,
    Sequence,
)
from contextlib import aclosing

from app.domain.market import (
    Candle,
    CandleInterval,
    CandleStreamProvider,
    Quote,
    QuoteStreamProvider,
)


class MarketStreamService:
    def __init__(
        self,
        candle_provider: CandleStreamProvider,
        quote_provider: QuoteStreamProvider,
    ) -> None:
        self._candle_provider = (
            candle_provider
        )

        self._quote_provider = (
            quote_provider
        )

    async def stream_candles(
        self,
        instrument_ids: Sequence[str],
        interval: CandleInterval,
    ) -> AsyncIterator[Candle]:
        stream = (
            self._candle_provider
            .stream_candles(
                instrument_ids,
                interval,
            )
        )

        async with aclosing(stream):
            async for candle in stream:
                yield candle

    async def stream_quotes(
        self,
        instrument_ids: Sequence[str],
    ) -> AsyncIterator[Quote]:
        stream = (
            self._quote_provider
            .stream_quotes(
                instrument_ids
            )
        )

        async with aclosing(stream):
            async for quote in stream:
                yield quote