import httpx
import pytest

from app.providers.binance.client import BinanceClient
from app.providers.binance.exceptions import (
    BinanceNetworkError,
    BinanceRateLimitError,
    BinanceResponseError,
)

@pytest.mark.asyncio
async def test_rate_limit_becomes_binance_rate_limit_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=429,
            json={"code": -1003, "msg": "Too many requests"},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with BinanceClient(transport=transport) as client:
        with pytest.raises(BinanceRateLimitError):
            await client.get_ticker_24h("BTCUSDT")

@pytest.mark.asyncio
async def test_server_error_becomes_binance_response_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=500,
            json={"msg": "Internal server error"},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with BinanceClient(transport=transport) as client:
        with pytest.raises(BinanceResponseError):
            await client.get_ticker_24h("BTCUSDT")

@pytest.mark.asyncio
async def test_network_failure_becomes_binance_network_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            "Simulated connection failure.",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with BinanceClient(transport=transport) as client:
        with pytest.raises(BinanceNetworkError):
            await client.get_ticker_24h("BTCUSDT")


@pytest.mark.asyncio
async def test_timeout_becomes_binance_network_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout(
            "Simulated timeout.",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with BinanceClient(transport=transport) as client:
        with pytest.raises(BinanceNetworkError):
            await client.get_ticker_24h("BTCUSDT")


@pytest.mark.asyncio
async def test_invalid_json_becomes_binance_response_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            content=b"not-json",
            headers={"Content-Type": "application/json"},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with BinanceClient(transport=transport) as client:
        with pytest.raises(BinanceResponseError):
            await client.get_ticker_24h("BTCUSDT")