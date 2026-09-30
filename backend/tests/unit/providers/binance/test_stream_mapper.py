from decimal import Decimal

from app.domain.market import CandleInterval
from app.providers.binance.mapper import BinanceMapper
from app.providers.binance.stream_mapper import (
    BinanceStreamMapper,
)


def make_instrument():
    return BinanceMapper.instrument(
        {
            "symbol": "BTCUSDT",
            "status": "TRADING",
            "baseAsset": "BTC",
            "quoteAsset": "USDT",
        }
    )


def test_stream_candle_maps_binance_kline_event() -> None:
    instrument = make_instrument()

    event = {
        "e": "kline",
        "E": 1704067250000,
        "s": "BTCUSDT",
        "k": {
            "t": 1704067200000,
            "T": 1704067259999,
            "s": "BTCUSDT",
            "i": "1m",
            "o": "42000.10000000",
            "c": "42100.40000000",
            "h": "42200.20000000",
            "l": "41900.30000000",
            "v": "12.34567890",
            "q": "518000.12345678",
            "x": False,
        },
    }

    candle = BinanceStreamMapper.candle(
        event,
        instrument,
    )

    assert candle.instrument_id == "BTC-USDT"
    assert candle.interval == CandleInterval.ONE_MINUTE

    assert candle.open == Decimal("42000.10000000")
    assert candle.high == Decimal("42200.20000000")
    assert candle.low == Decimal("41900.30000000")
    assert candle.close == Decimal("42100.40000000")

    assert candle.volume == Decimal("12.34567890")
    assert candle.quote_volume == Decimal(
        "518000.12345678"
    )

    assert candle.is_closed is False
    assert candle.source == "binance"


def test_stream_candle_preserves_closed_state() -> None:
    instrument = make_instrument()

    event = {
        "e": "kline",
        "E": 1704067260000,
        "s": "BTCUSDT",
        "k": {
            "t": 1704067200000,
            "T": 1704067259999,
            "s": "BTCUSDT",
            "i": "1m",
            "o": "42000",
            "c": "42100",
            "h": "42200",
            "l": "41900",
            "v": "10",
            "q": "420000",
            "x": True,
        },
    }

    candle = BinanceStreamMapper.candle(
        event,
        instrument,
    )

    assert candle.is_closed is True

def test_stream_quote_maps_binance_ticker_event() -> None:
    instrument = make_instrument()

    event = {
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
    }

    quote = BinanceStreamMapper.quote(
        event,
        instrument,
    )

    assert quote.instrument_id == (
        "BTC-USDT"
    )

    assert quote.bid == Decimal(
        "42100.30"
    )

    assert quote.ask == Decimal(
        "42100.50"
    )

    assert quote.last == Decimal(
        "42100.40"
    )

    assert quote.change_percent_24h == (
        Decimal("0.240")
    )

    assert quote.source == "binance"