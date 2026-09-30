from collections.abc import (
    AsyncIterator,
    Sequence,
)
from contextlib import aclosing

from app.domain.market import (
    Candle,
    CandleInterval,
    CandleStreamProvider,
)


class MarketStreamService:
    def __init__(
        self,
        provider: CandleStreamProvider,
    ) -> None:
        self._provider = provider

    async def stream_candles(
        self,
        instrument_ids: Sequence[str],
        interval: CandleInterval,
    ) -> AsyncIterator[Candle]:
        stream = self._provider.stream_candles(
            instrument_ids,
            interval,
        )

        async with aclosing(stream):
            async for candle in stream:
                yield candle