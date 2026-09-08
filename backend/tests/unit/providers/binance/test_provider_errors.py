import pytest

from app.domain.market import CandleInterval
from app.domain.market.exceptions import (
    InstrumentNotFoundError,
    MarketDataUnavailableError
)
from app.providers.binance.exceptions import BinanceNetworkError
from app.providers.binance.provider import BinanceMarketDataProvider

class FakeBinanceClient:
    async def close(self) -> None:
        pass

    async def get_exchange_info(
        self,
        symbol: str | None = None,
    ) -> dict:
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

    async def get_ticker_24h(
        self,
        symbol: str,
    ) -> dict:
        raise BinanceNetworkError(
            "Simulated Binance network failure."
        )

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 500,
    ) -> list:
        raise BinanceNetworkError(
            "Simulated Binance network failure."
        )

class BrokenRegistryClient(FakeBinanceClient):
    async def get_exchange_info(
        self,
        symbol: str | None = None,
    ) -> dict:
        raise BinanceNetworkError(
            "Simulated registry failure"
        )

@pytest.mark.asyncio
async def test_unknown_instrument_raises_domain_error() -> None:
    provider = BinanceMarketDataProvider(
        client=FakeBinanceClient()
    )

    with pytest.raises(InstrumentNotFoundError) as exc_info:
        await provider.get_instrument("ETH-USDT")

    assert exc_info.value.instrument_id == "ETH-USDT"

@pytest.mark.asyncio
async def test_quote_provider_failure_becomes_market_error() -> None:
    provider = BinanceMarketDataProvider(
        client=FakeBinanceClient()
    )

    with pytest.raises(MarketDataUnavailableError):
        await provider.get_quote("BTC-USDT")

@pytest.mark.asyncio
async def test_candle_provider_failure_becomes_market_error() -> None:
    provider = BinanceMarketDataProvider(
        client=FakeBinanceClient()
    )

    with pytest.raises(MarketDataUnavailableError):
        await provider.get_candles(
            "BTC-USDT",
            CandleInterval.ONE_HOUR,
        )

@pytest.mark.asyncio
async def test_registry_failure_becomes_market_error() -> None:
    provider = BinanceMarketDataProvider(
        client=BrokenRegistryClient()
    )

    with pytest.raises(MarketDataUnavailableError):
        await provider.get_instrument("BTC-USDT")
