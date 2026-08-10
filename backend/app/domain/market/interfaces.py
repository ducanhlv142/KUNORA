from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence

from .enums import CandleInterval
from .models import Candle, Instrument, Quote, Trade

class MarketDataProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider name."""
        raise NotImplementedError

    @abstractmethod
    async def get_instruments(self) -> Sequence[Instrument]:
        raise NotImplementedError

    @abstractmethod
    async def get_quotes(self, instrument_id: str) -> Quote:
        raise NotImplementedError

    @abstractmethod
    async def get_candles(
        self, 
        instrument_id: str, 
        interval: CandleInterval, 
        limit: int = 500,
    ) -> Sequence[Candle]:
        raise NotImplementedError

    @abstractmethod
    async def stream_quotes(
        self,
        instrument_ids: Sequence[str]
    ) -> AsyncIterator[Quote]:
        raise NotImplementedError

    @abstractmethod
    async def stream_trades(
        self,
        instrument_ids: Sequence[str]
    ) -> AsyncIterator[Trade]:
        raise NotImplementedError