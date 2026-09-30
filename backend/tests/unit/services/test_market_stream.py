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
    Quote,
    QuoteStreamProvider,
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

class FakeQuoteStreamProvider(
    QuoteStreamProvider
):
    def __init__(
        self,
        quotes: list[Quote],
    ) -> None:
        self.quotes = quotes
        self.instrument_ids: tuple[str, ...] = ()
        self.closed = False

    @property
    def name(self) -> str:
        return "fake"

    async def stream_quotes(
        self,
        instrument_ids: Sequence[str],
    ) -> AsyncIterator[Quote]:
        self.instrument_ids = tuple(
            instrument_ids
        )

        try:
            for quote in self.quotes:
                yield quote
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

def make_quote() -> Quote:
    return Quote(
        instrument_id="BTC-USDT",

        bid=Decimal("83749"),
        ask=Decimal("83751"),
        last=Decimal("83750"),

        open_24h=Decimal("83000"),
        high_24h=Decimal("84000"),
        low_24h=Decimal("82000"),

        price_change_24h=Decimal("750"),
        change_percent_24h=Decimal("0.90"),

        base_volume_24h=Decimal("1000"),
        quote_volume_24h=Decimal(
            "83750000"
        ),

        timestamp=datetime(
            2026,
            9,
            30,
            10,
            0,
            tzinfo=timezone.utc,
        ),

        source="fake",
    )

@pytest.mark.asyncio
async def test_stream_service_forwards_candle() -> None:
    provider = FakeCandleStreamProvider(
        [make_candle()]
    )

    service = MarketStreamService(
        candle_provider=provider,
        quote_provider=FakeQuoteStreamProvider(
            []
        ),
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

@pytest.mark.asyncio
async def test_stream_service_forwards_quote() -> None:
    quote_provider = (
        FakeQuoteStreamProvider(
            [make_quote()]
        )
    )

    service = MarketStreamService(
        candle_provider=(
            FakeCandleStreamProvider([])
        ),
        quote_provider=quote_provider,
    )

    stream = service.stream_quotes(
        ["BTC-USDT"]
    )

    async with aclosing(stream):
        quote = await anext(stream)

    assert quote.instrument_id == (
        "BTC-USDT"
    )

    assert quote.last == Decimal(
        "83750"
    )

    assert quote.bid == Decimal(
        "83749"
    )

    assert quote.ask == Decimal(
        "83751"
    )

    assert quote_provider.instrument_ids == (
        "BTC-USDT",
    )

    assert quote_provider.closed is True