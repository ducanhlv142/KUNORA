from collections.abc import (
    AsyncIterator,
    Sequence,
)
from contextlib import aclosing
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.domain.market import (
    Candle,
    CandleInterval,
    CandleStreamProvider,
)
from app.services.market_stream import (
    MarketStreamService,
)


class FakeCandleStreamProvider(
    CandleStreamProvider
):
    def __init__(
        self,
        candles: list[Candle],
    ) -> None:
        self.candles = candles
        self.instrument_ids: tuple[str, ...] = ()
        self.interval: CandleInterval | None = None
        self.closed = False

    @property
    def name(self) -> str:
        return "fake"

    async def stream_candles(
        self,
        instrument_ids: Sequence[str],
        interval: CandleInterval,
    ) -> AsyncIterator[Candle]:
        self.instrument_ids = tuple(
            instrument_ids
        )
        self.interval = interval

        try:
            for candle in self.candles:
                yield candle
        finally:
            self.closed = True


def make_candle() -> Candle:
    return Candle(
        instrument_id="BTC-USDT",
        interval=CandleInterval.ONE_MINUTE,
        open_time=datetime(
            2026,
            9,
            30,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        close_time=datetime(
            2026,
            9,
            30,
            10,
            0,
            59,
            tzinfo=timezone.utc,
        ),
        open=Decimal("83700"),
        high=Decimal("83800"),
        low=Decimal("83600"),
        close=Decimal("83750"),
        volume=Decimal("10"),
        quote_volume=Decimal("837500"),
        is_closed=False,
        source="fake",
    )


@pytest.mark.asyncio
async def test_stream_service_forwards_candle() -> None:
    provider = FakeCandleStreamProvider(
        [make_candle()]
    )

    service = MarketStreamService(
        provider
    )

    stream = service.stream_candles(
        ["BTC-USDT"],
        CandleInterval.ONE_MINUTE,
    )

    async with aclosing(stream):
        candle = await anext(stream)

    assert candle.instrument_id == "BTC-USDT"
    assert candle.close == Decimal("83750")

    assert provider.instrument_ids == (
        "BTC-USDT",
    )

    assert provider.interval == (
        CandleInterval.ONE_MINUTE
    )

    assert provider.closed is True