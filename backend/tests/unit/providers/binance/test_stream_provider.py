from collections.abc import AsyncIterator
from typing import Any
from decimal import Decimal

import pytest

from app.domain.market import (
    CandleInterval,
)
from app.providers.binance.provider import (
    BinanceMarketDataProvider,
)
from app.providers.binance.stream_provider import (
    BinanceCandleStreamProvider,
    BinanceQuoteStreamProvider,
)


class FakeRegistryClient:
    async def close(self) -> None:
        pass

    async def get_exchange_info(
        self,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        return {
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "TRADING",
                    "baseAsset": "BTC",
                    "quoteAsset": "USDT",
                }
            ]
        }


class FakeStreamClient:
    def __init__(
        self,
        messages: list[dict[str, Any]],
    ) -> None:
        self.messages = messages
        self.requested_streams: list[str] = []

    @staticmethod
    def kline_stream(
        symbol: str,
        interval: str,
    ) -> str:
        return (
            f"{symbol.lower()}"
            f"@kline_{interval}"
        )

    async def stream(
        self,
        streams: list[str],
    ) -> AsyncIterator[dict[str, Any]]:
        self.requested_streams = list(
            streams
        )

        for message in self.messages:
            yield message

    @staticmethod
    def ticker_stream(
        symbol: str,
    ) -> str:
        return (
            f"{symbol.lower()}@ticker"
        )


@pytest.mark.asyncio
async def test_stream_provider_maps_live_candle() -> None:
    market_provider = (
        BinanceMarketDataProvider(
            client=FakeRegistryClient()
        )
    )

    message = {
        "stream": "btcusdt@kline_1m",
        "data": {
            "e": "kline",
            "E": 1704067250000,
            "s": "BTCUSDT",
            "k": {
                "t": 1704067200000,
                "T": 1704067259999,
                "s": "BTCUSDT",
                "i": "1m",
                "o": "42000.10",
                "c": "42100.40",
                "h": "42200.20",
                "l": "41900.30",
                "v": "12.345",
                "q": "518000.12",
                "x": False,
            },
        },
    }

    stream_client = FakeStreamClient(
        [message]
    )

    provider = BinanceCandleStreamProvider(
        market_data_provider=market_provider,
        client=stream_client,
    )

    candles = provider.stream_candles(
        ["BTC-USDT"],
        CandleInterval.ONE_MINUTE,
    )

    candle = await anext(candles)

    await candles.aclose()

    assert candle.instrument_id == (
        "BTC-USDT"
    )

    assert candle.interval == (
        CandleInterval.ONE_MINUTE
    )

    assert candle.close == Decimal(
        "42100.40"
    )

    assert candle.is_closed is False

    assert stream_client.requested_streams == [
        "btcusdt@kline_1m"
    ]


@pytest.mark.asyncio
async def test_stream_provider_requires_instrument() -> None:
    market_provider = (
        BinanceMarketDataProvider(
            client=FakeRegistryClient()
        )
    )

    provider = BinanceCandleStreamProvider(
        market_data_provider=market_provider,
        client=FakeStreamClient([]),
    )

    candles = provider.stream_candles(
        [],
        CandleInterval.ONE_MINUTE,
    )

    with pytest.raises(
        ValueError,
        match="At least one instrument",
    ):
        await anext(candles)

@pytest.mark.asyncio
async def test_quote_stream_provider_maps_live_quote() -> None:
    market_provider = (
        BinanceMarketDataProvider(
            client=FakeRegistryClient()
        )
    )

    message = {
        "stream": "btcusdt@ticker",
        "data": {
            "e": "24hrTicker",
            "E": 1704067250000,
            "s": "BTCUSDT",

            "p": "100.50",
            "P": "0.240",

            "c": "42100.40",

            "b": "42100.30",
            "a": "42100.50",

            "o": "42000.00",
            "h": "42500.00",
            "l": "41800.00",

            "v": "1234.5678",
            "q": "52000000.12",
        },
    }

    stream_client = FakeStreamClient(
        [message]
    )

    provider = BinanceQuoteStreamProvider(
        market_data_provider=market_provider,
        client=stream_client,
    )

    quotes = provider.stream_quotes(
        ["BTC-USDT"]
    )

    quote = await anext(quotes)

    await quotes.aclose()

    assert quote.instrument_id == (
        "BTC-USDT"
    )

    assert quote.last == Decimal(
        "42100.40"
    )

    assert quote.bid == Decimal(
        "42100.30"
    )

    assert quote.ask == Decimal(
        "42100.50"
    )

    assert stream_client.requested_streams == [
        "btcusdt@ticker"
    ]


@pytest.mark.asyncio
async def test_quote_stream_provider_requires_instrument() -> None:
    market_provider = (
        BinanceMarketDataProvider(
            client=FakeRegistryClient()
        )
    )

    provider = BinanceQuoteStreamProvider(
        market_data_provider=market_provider,
        client=FakeStreamClient([]),
    )

    quotes = provider.stream_quotes([])

    with pytest.raises(
        ValueError,
        match="At least one instrument",
    ):
        await anext(quotes)