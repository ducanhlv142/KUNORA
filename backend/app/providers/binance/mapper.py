from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.domain.market import (
    Asset,
    AssetClass,
    Candle,
    CandleInterval,
    Instrument,
    InstrumentType,
    MarketStatus,
    Quote,
)

class BinanceMapper:
    SOURCE = "binance"
    VENUE = "BINANCE"

    @staticmethod
    def _asset(symbol: str) -> Asset:
        symbol = symbol.upper()

        return Asset(
            id=symbol,
            symbol=symbol,
            name=symbol,
            asset_class=AssetClass.CRYPTO,
        )

    @classmethod
    def instrument(cls, data: dict[str, Any]) -> Instrument:
        base_symbol = data["baseAsset"]
        quote_symbol = data["quoteAsset"]

        base_asset = cls._asset(base_symbol)
        quote_asset = cls._asset(quote_symbol)

        status = (
            MarketStatus.ACTIVE
            if data["status"] == "TRADING"
            else MarketStatus.UNKNOWN
        )

        return Instrument(
            id=f"{base_symbol}-{quote_symbol}",
            symbol=f"{base_symbol}/{quote_symbol}",
            base_asset=base_asset,
            quote_asset=quote_asset,
            instrument_type=InstrumentType.SPOT,
            venue=cls.VENUE,
            status=status,
        )

    @classmethod
    def quote(
        cls,
        data: dict[str, Any],
        instrument: Instrument,
    ) -> Quote:
        return Quote(
            instrument_id=instrument.id,
            last=Decimal(data["lastPrice"]),
            open_24h=Decimal(data["openPrice"]),
            high_24h=Decimal(data["highPrice"]),
            low_24h=Decimal(data["lowPrice"]),
            price_change_24h=Decimal(data["priceChange"]),
            change_percent_24h=Decimal(data["priceChangePercent"]),
            base_volume_24h=Decimal(data["volume"]),
            quote_volume_24h=Decimal(data["quoteVolume"]),
            timestamp=datetime.fromtimestamp(
                data["closeTime"] / 1000, 
                tz=timezone.utc,
            ),
            source=cls.SOURCE,
        )

    @classmethod
    def candle(
        cls,
        data: dict[str, Any],
        instrument: Instrument,
        interval: CandleInterval,
    ) -> Candle:
        close_time = datetime.fromtimestamp(
            data[6] / 1000, 
            tz=timezone.utc
        )

        return Candle(
            instrument_id=instrument.id,
            interval=interval,
            open_time=datetime.fromtimestamp(
                data[0] / 1000, 
                tz=timezone.utc,
            ),
            close_time=close_time,
            open=Decimal(data[1]),
            high=Decimal(data[2]),
            low=Decimal(data[3]),
            close=Decimal(data[4]),
            volume=Decimal(data[5]),
            quote_volume=Decimal(data[7]),
            is_closed=datetime.now(timezone.utc) > close_time,
            source=cls.SOURCE,
        )
