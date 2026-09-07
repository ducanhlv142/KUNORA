from datetime import datetime, timezone
from decimal import Decimal

from app.domain.market import (
    CandleInterval,
    MarketStatus,
)
from app.providers.binance.mapper import BinanceMapper

def make_instrument():
    return BinanceMapper.instrument(
        {
            "symbol": "BTCUSDT",
            "status": "TRADING",
            "baseAsset": "BTC",
            "quoteAsset": "USDT",
        }
    )

def test_instrument_maps_binance_symbol_to_kunora_domain() -> None:
    instrument = make_instrument()

    assert instrument.id == "BTC-USDT"
    assert instrument.symbol == "BTC/USDT"

    assert instrument.base_asset.id == "BTC"
    assert instrument.quote_asset is not None
    assert instrument.quote_asset.id == "USDT"

    assert instrument.venue == "BINANCE"
    assert instrument.status == MarketStatus.ACTIVE

def test_quote_preserves_decimal_precision_and_timestamp() -> None:
    instrument = make_instrument()

    raw_quote = {
        "lastPrice": "79624.81000000",
        "openPrice": "80009.71000000",
        "highPrice": "80559.99000000",
        "lowPrice": "79233.00000000",
        "priceChange": "-384.90000000",
        "priceChangePercent": "-0.481",
        "volume": "9703.35769000",
        "quoteVolume": "775330218.48796710",
        "closeTime": 1704067200123,
    }

    quote = BinanceMapper.quote(
        raw_quote,
        instrument,
    )

    assert quote.instrument_id == "BTC-USDT"

    assert quote.last == Decimal("79624.81000000")
    assert quote.price_change_24h == Decimal("-384.90000000")
    assert quote.change_percent_24h == Decimal("-0.481")

    assert quote.base_volume_24h == Decimal("9703.35769000")
    assert quote.quote_volume_24h == Decimal("775330218.48796710")

    assert quote.timestamp == datetime.fromtimestamp(
        raw_quote["closeTime"] / 1000, 
        tz=timezone.utc
    )

    assert quote.source == "binance"

def test_closed_candle_maps_ohlcv_correctly() -> None:
    instrument = make_instrument()

    raw_candle = [
        1704067200000,          # open time
        "42000.10000000",       # open
        "42500.20000000",       # high
        "41800.30000000",       # low
        "42300.40000000",       # close
        "123.45678900",         # base volume
        1704070799999,          # close time
        "5200000.12345678",     # quote volume
    ]

    candle = BinanceMapper.candle(
        raw_candle,
        instrument,
        CandleInterval.ONE_HOUR,
    )

    assert candle.instrument_id == "BTC-USDT"
    assert candle.interval == CandleInterval.ONE_HOUR

    assert candle.open == Decimal("42000.10000000")
    assert candle.high == Decimal("42500.20000000")
    assert candle.low == Decimal("41800.30000000")
    assert candle.close == Decimal("42300.40000000")

    assert candle.volume == Decimal("123.45678900")
    assert candle.quote_volume == Decimal("5200000.12345678")

    assert candle.is_closed is True
    assert candle.source == "binance"

def test_future_candle_is_not_closed() -> None:
    instrument = make_instrument()

    raw_candle = [
        4102444800000,      # 2100-01-01 00:00 UTC
        "42000",
        "42500",
        "41800",
        "42300",
        "100",
        4102448399999,      # 2100-01-01 00:59:59.999 UTC
        "4200000",
    ]

    candle = BinanceMapper.candle(
        raw_candle,
        instrument,
        CandleInterval.ONE_HOUR,
    )

    assert candle.is_closed is False