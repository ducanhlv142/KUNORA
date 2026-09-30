from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)

from app.domain.market import CandleInterval


class StreamChannel(StrEnum):
    QUOTES = "quotes"
    CANDLES = "candles"
    TRADES = "trades"


class SubscriptionAction(StrEnum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


class SubscriptionCommand(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    type: SubscriptionAction
    channel: StreamChannel

    instrument_id: str

    interval: CandleInterval | None = None

    @field_validator("instrument_id")
    @classmethod
    def normalize_instrument_id(
        cls,
        value: str,
    ) -> str:
        return value.strip().upper()

    @model_validator(mode="after")
    def validate_channel_options(
        self,
    ) -> Self:
        if (
            self.channel is StreamChannel.CANDLES
            and self.interval is None
        ):
            raise ValueError(
                "interval is required for candle subscriptions"
            )

        if (
            self.channel is not StreamChannel.CANDLES
            and self.interval is not None
        ):
            raise ValueError(
                "interval is only valid for candle subscriptions"
            )

        return self