import pytest

from app.providers.binance.exceptions import (
    BinanceResponseError,
)
from app.providers.binance.stream_client import (
    BinanceStreamClient,
)


def test_kline_stream_name() -> None:
    stream = BinanceStreamClient.kline_stream(
        "BTCUSDT",
        "1m",
    )

    assert stream == "btcusdt@kline_1m"


def test_build_combined_stream_uri() -> None:
    uri = BinanceStreamClient.build_uri(
        [
            "ETHUSDT@kline_1m",
            "BTCUSDT@kline_1m",
        ]
    )

    assert uri == (
        "wss://stream.binance.com:443/stream"
        "?streams=btcusdt@kline_1m/"
        "ethusdt@kline_1m"
    )


def test_build_uri_removes_duplicates() -> None:
    uri = BinanceStreamClient.build_uri(
        [
            "btcusdt@kline_1m",
            "BTCUSDT@kline_1m",
        ]
    )

    assert uri.count(
        "btcusdt@kline_1m"
    ) == 1


def test_build_uri_rejects_empty_streams() -> None:
    with pytest.raises(ValueError):
        BinanceStreamClient.build_uri([])


def test_decode_combined_stream_message() -> None:
    payload = BinanceStreamClient.decode_message(
        """
        {
          "stream": "btcusdt@kline_1m",
          "data": {
            "e": "kline",
            "s": "BTCUSDT"
          }
        }
        """
    )

    assert payload["stream"] == (
        "btcusdt@kline_1m"
    )

    assert payload["data"]["e"] == "kline"


def test_decode_invalid_json_raises_provider_error() -> None:
    with pytest.raises(
        BinanceResponseError
    ):
        BinanceStreamClient.decode_message(
            "definitely-not-json"
        )


def test_decode_non_object_payload_is_rejected() -> None:
    with pytest.raises(
        BinanceResponseError
    ):
        BinanceStreamClient.decode_message(
            '["unexpected"]'
        )

def test_ticker_stream_name() -> None:
    stream = (
        BinanceStreamClient.ticker_stream(
            "BTCUSDT"
        )
    )

    assert stream == "btcusdt@ticker"

