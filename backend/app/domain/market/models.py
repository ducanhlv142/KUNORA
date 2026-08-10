from datetime import datetime
from typing import Sequence
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import (
    AssetClass,
    CandleInterval,
    InstrumentType,
    MarketStatus,
    TradeSide,
)

class DomainModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

class Asset(DomainModel):
    id: str
    symbol: str
    name: str
    asset_class: AssetClass

    @field_validator("id", "symbol")
    @classmethod
    def normalize_identifiers(cls, value: str) -> str:
        return value.upper()

class Instrument(DomainModel):
    id: str
    symbol: str

    base_asset: Asset
    quote_asset: Asset | None = None

    instrument_type: InstrumentType
    venue: str
    status: MarketStatus = MarketStatus.UNKNOWN

    @field_validator("id", "symbol")
    @classmethod
    def normalize_identifiers(cls, value: str) -> str:
        return value.upper()

class Quote(DomainModel):
    instrument_id: str

    bid: Decimal | None = None
    ask: Decimal | None = None
    last: Decimal

    open_24h: Decimal | None = None
    high_24h: Decimal | None = None
    low_24h: Decimal | None = None
    volume_24h: Decimal | None = None
    change_24h: Decimal | None = None

    timestamp: datetime
    source: str

    @field_validator("instrument_id")
    @classmethod
    def normalize_instrument_id(cls, value: str) -> str:
        return value.upper()

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must be timezone-aware")
        return value


class Candle(DomainModel):
    instrument_id: str
    interval: CandleInterval

    open_time: datetime
    close_time: datetime

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    source: str

    @field_validator("instrument_id")
    @classmethod
    def normalize_instrument_id(cls, value: str) -> str:
        return value.upper()

    @field_validator("open_time", "close_time")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must be timezone-aware")
        return value

class Trade(DomainModel):
    instrument_id: str
    trade_id: str | None = None

    price: Decimal
    quantity: Decimal
    side: TradeSide = TradeSide.UNKNOWN

    timestamp: datetime
    source: str

    @field_validator("instrument_id")
    @classmethod
    def normalize_instrument_id(cls, value: str) -> str:
        return value.upper()

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must be timezone-aware")
        return value

class OrderBookLevel(DomainModel):
    price: Decimal
    quantity: Decimal

class OrderBook(DomainModel):
    instrument_id: str

    bids: Sequence[OrderBookLevel] = Field(default_factory=tuple)
    asks: Sequence[OrderBookLevel] = Field(default_factory=tuple)

    sequence: int | None = None
    timestamp: datetime
    source: str

    @field_validator("instrument_id")
    @classmethod
    def normalize_instrument_id(cls, value: str) -> str:
        return value.upper()

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must be timezone-aware")
        return value