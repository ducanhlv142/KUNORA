import json
from collections.abc import AsyncIterator, Sequence
from typing import Any

from websockets.asyncio.client import connect
from websockets.exceptions import (
    ConnectionClosed,
    InvalidHandshake,
)

from .exceptions import (
    BinanceNetworkError,
    BinanceResponseError,
)


class BinanceStreamClient:
    BASE_URL = "wss://stream.binance.com:443/stream"

    def __init__(
        self,
        open_timeout: float = 10.0,
        close_timeout: float = 10.0,
    ) -> None:
        self._open_timeout = open_timeout
        self._close_timeout = close_timeout

    @staticmethod
    def kline_stream(
        symbol: str,
        interval: str,
    ) -> str:
        return (
            f"{symbol.strip().lower()}"
            f"@kline_{interval}"
        )

    @classmethod
    def build_uri(
        cls,
        streams: Sequence[str],
    ) -> str:
        normalized_streams = sorted(
            {
                stream.strip().lower()
                for stream in streams
                if stream.strip()
            }
        )

        if not normalized_streams:
            raise ValueError(
                "At least one stream is required."
            )

        joined_streams = "/".join(
            normalized_streams
        )

        return (
            f"{cls.BASE_URL}"
            f"?streams={joined_streams}"
        )

    @staticmethod
    def decode_message(
        raw_message: str | bytes,
    ) -> dict[str, Any]:
        try:
            payload = json.loads(
                raw_message
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise BinanceResponseError(
                "Binance WebSocket returned invalid JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise BinanceResponseError(
                "Binance WebSocket returned an invalid payload."
            )

        return payload

    async def stream(
        self,
        streams: Sequence[str],
    ) -> AsyncIterator[dict[str, Any]]:
        uri = self.build_uri(streams)

        try:
            async for websocket in connect(
                uri,
                open_timeout=self._open_timeout,
                close_timeout=self._close_timeout,
                ping_interval=20,
                ping_timeout=20,
                max_size=1_048_576,
            ):
                try:
                    async for raw_message in websocket:
                        payload = self.decode_message(
                            raw_message
                        )

                        data = payload.get("data")

                        if (
                            isinstance(data, dict)
                            and data.get("e") == "serverShutdown"
                        ):
                            break

                        yield payload

                except ConnectionClosed:
                    continue

                finally:
                    await websocket.close()

        except InvalidHandshake as exc:
            raise BinanceResponseError(
                "Binance WebSocket handshake failed."
            ) from exc

        except OSError as exc:
            raise BinanceNetworkError(
                "Unable to connect to Binance WebSocket."
            ) from exc