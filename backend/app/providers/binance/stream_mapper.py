from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.domain.market import (
    Candle,
    CandleInterval,
    Instrument,
)


class BinanceStreamMapper:
    SOURCE = "binance"

    @classmethod
    def candle(
        cls,
        data: dict[str, Any],
        instrument: Instrument,
    ) -> Candle:
        kline = data["k"]

        interval = CandleInterval(
            kline["i"]
        )

        return Candle(
            instrument_id=instrument.id,
            interval=interval,
            open_time=datetime.fromtimestamp(
                kline["t"] / 1000,
                tz=timezone.utc,
            ),
            close_time=datetime.fromtimestamp(
                kline["T"] / 1000,
                tz=timezone.utc,
            ),
            open=Decimal(kline["o"]),
            high=Decimal(kline["h"]),
            low=Decimal(kline["l"]),
            close=Decimal(kline["c"]),
            volume=Decimal(kline["v"]),
            quote_volume=Decimal(kline["q"]),
            is_closed=bool(kline["x"]),
            source=cls.SOURCE,
        )