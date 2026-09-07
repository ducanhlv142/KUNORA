from typing import Any

import httpx

class BinanceClient:
    BASE_URL = "https://data-api.binance.vision"

    def __init__(self, timeout: float = 10.0) -> None:
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
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
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

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

