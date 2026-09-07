import pytest

from app.domain.market import CandleInterval
from app.providers.binance.provider import BinanceMarketDataProvider

@pytest.mark.integration
@pytest.mark.asyncio

async def test_binance_provider_returns_live_market_data() -> None:
    async with BinanceMarketDataProvider() as provider:
        instrument = await provider.get_instrument("BTC-USDT")
        quote = await provider.get_quote("BTC-USDT")
        candles = await provider.get_candles(
            "BTC-USDT", 
            CandleInterval.ONE_HOUR, 
            limit=2,
        )

        assert instrument.id == "BTC-USDT"
        assert instrument.venue == "BINANCE"

        assert quote.instrument_id == "BTC-USDT"
        assert quote.last > 0

        assert len(candles) == 2

        for candle in candles:
            assert candle.instrument_id == "BTC-USDT"
            assert candle.high >= candle.low
            assert candle.volume >= 0
