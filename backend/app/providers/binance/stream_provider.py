from collections.abc import AsyncIterator, Sequence

from app.domain.market import (
    Candle,
    CandleInterval,
    CandleStreamProvider,
    Instrument,
    MarketDataProvider,
)

from .stream_client import BinanceStreamClient
from .stream_mapper import BinanceStreamMapper


class BinanceCandleStreamProvider(
    CandleStreamProvider
):
    def __init__(
        self,
        market_data_provider: MarketDataProvider,
        client: BinanceStreamClient | None = None,
    ) -> None:
        self._market_data_provider = (
            market_data_provider
        )

        self._client = (
            client
            or BinanceStreamClient()
        )

    @property
    def name(self) -> str:
        return "binance"

    @staticmethod
    def _symbol(
        instrument: Instrument,
    ) -> str:
        quote_asset = instrument.quote_asset

        if quote_asset is None:
            raise ValueError(
                "Instrument requires a quote asset."
            )

        return (
            f"{instrument.base_asset.symbol}"
            f"{quote_asset.symbol}"
        )

    async def stream_candles(
        self,
        instrument_ids: Sequence[str],
        interval: CandleInterval,
    ) -> AsyncIterator[Candle]:
        if not instrument_ids:
            raise ValueError(
                "At least one instrument is required."
            )

        instruments_by_symbol: dict[
            str,
            Instrument,
        ] = {}

        streams: list[str] = []

        for instrument_id in instrument_ids:
            instrument = (
                await self._market_data_provider
                .get_instrument(
                    instrument_id
                )
            )

            symbol = self._symbol(
                instrument
            ).upper()

            instruments_by_symbol[
                symbol
            ] = instrument

            streams.append(
                self._client.kline_stream(
                    symbol,
                    interval.value,
                )
            )

        async for payload in self._client.stream(
            streams
        ):
            data = payload.get("data")

            if not isinstance(data, dict):
                continue

            if data.get("e") != "kline":
                continue

            symbol = data.get("s")

            if not isinstance(symbol, str):
                continue

            instrument = (
                instruments_by_symbol.get(
                    symbol.upper()
                )
            )

            if instrument is None:
                continue

            candle = BinanceStreamMapper.candle(
                data,
                instrument,
            )

            # Defensive check in case the upstream
            # stream doesn't match our subscription.
            if candle.interval != interval:
                continue

            yield candle