from app.domain.market import (
    Candle,
    CandleInterval,
    Instrument,
    MarketDataProvider,
    Quote,
)

from app.domain.market.exceptions import (
    InstrumentNotFoundError,
    MarketDataUnavailableError,
)

from .client import BinanceClient
from .mapper import BinanceMapper
from .exceptions import BinanceError
class BinanceMarketDataProvider(MarketDataProvider):

    def __init__(self, client: BinanceClient | None = None) -> None:
        self._client = client or BinanceClient()

        #Kunora instrucment ID -> Binance symbol
        self._symbols: dict[str, str] = {}

        #Kunora instrument ID -> Domain instrument
        self._instruments: dict[str, Instrument] = {}

    @property
    def name(self) -> str:
        return "binance"

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "BinanceMarketDataProvider":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def get_instruments(self) -> list[Instrument]:
            await self._ensure_registry()
            return list(self._instruments.values())

    async def get_instrument(
            self,
            instrument_id: str,
    ) -> Instrument:
        await self._ensure_registry()

        normalized_id = instrument_id.upper()

        try:
            return self._instruments[normalized_id]
        except KeyError as exc:
            raise InstrumentNotFoundError(
                instrument_id
            ) from exc

    async def get_quote(
        self,
        instrument_id: str,
    ) -> Quote:
        instrument = await self.get_instrument(instrument_id)
        binance_symbol = self._symbols[instrument.id]

        try:
            raw_quote = await self._client.get_ticker_24h(
                binance_symbol
            )

        except BinanceError as exc:
                raise MarketDataUnavailableError() from exc

        return BinanceMapper.quote(
            raw_quote,
            instrument,
        )



    async def get_candles(
        self,
        instrument_id: str,
        interval: CandleInterval,
        limit: int = 500,
    ) -> list[Candle]:
        instrument = await self.get_instrument(instrument_id)
        binance_symbol = self._symbols[instrument.id]

        try:
            raw_candles = await self._client.get_klines(
                symbol=binance_symbol,
                interval=interval.value,
                limit=limit,
            )
        except BinanceError as exc:
                    raise MarketDataUnavailableError() from exc

        return [
            BinanceMapper.candle(
                raw,
                instrument,
                interval,
            )
            for raw in raw_candles
        ]

    async def _load_registry(self) -> None:
        try:
            exchange_info = await self._client.get_exchange_info()
        except BinanceError as exc:
            raise MarketDataUnavailableError() from exc

        self._instruments.clear()
        self._symbols.clear()

        for raw in exchange_info["symbols"]:
            instrument = BinanceMapper.instrument(raw)

            self._instruments[instrument.id] = instrument
            self._symbols[instrument.id] = raw["symbol"]

    async def _ensure_registry(self) -> None:
        if not self._instruments:
            await self._load_registry()