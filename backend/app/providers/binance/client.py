from typing import Any
from .exceptions import (
    BinanceNetworkError,
    BinanceRateLimitError,
    BinanceResponseError,
)

import httpx

class BinanceClient:
    BASE_URL = "https://data-api.binance.vision"

    def __init__(
        self,
        timeout: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            transport=transport,
            headers={
                "Accept": "application/json",
                "User-Agent": "KUNORA/0.1",
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "BinanceClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = await self._client.get(
                path,
                params=params,
            )

            if response.status_code == 429:
                raise BinanceRateLimitError(
                    "Binance rate limit exceeded."
                )
            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise BinanceNetworkError(
                "Binance request timed out."
            ) from exc

        except httpx.NetworkError as exc:
            raise BinanceNetworkError(
                "Unable to connect to Binance."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise BinanceResponseError(
                f"Binance returned HTTP {exc.response.status_code}."
            ) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise BinanceResponseError(
                "Binance returned an invalid JSON response."
            ) from exc

    async def get_exchange_info(
        self,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        params = {"symbol": symbol.upper()} if symbol else None

        return await self._get(
            "/api/v3/exchangeInfo",
            params=params,
        )

    async def get_ticker_24h(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        return await self._get(
            "/api/v3/ticker/24hr",
            params={
                "symbol": symbol.upper(),
                "type": "FULL",
            },
        )

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 500,
    ) -> list[list[Any]]:
        if not (1 <= limit <= 1000):
            raise ValueError("Limit must be between 1 and 1000")

        return await self._get(
            "/api/v3/klines",
            params={
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": limit,
            },
        )

