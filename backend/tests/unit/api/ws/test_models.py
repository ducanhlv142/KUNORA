import pytest
from pydantic import ValidationError

from app.api.ws.models import (
    StreamChannel,
    SubscriptionAction,
    SubscriptionCommand,
)
from app.domain.market import CandleInterval


def test_valid_candle_subscription() -> None:
    command = SubscriptionCommand(
        type="subscribe",
        channel="candles",
        instrument_id="btc-usdt",
        interval="1m",
    )

    assert command.type == SubscriptionAction.SUBSCRIBE
    assert command.channel == StreamChannel.CANDLES

    assert command.instrument_id == "BTC-USDT"
    assert command.interval == CandleInterval.ONE_MINUTE


def test_candle_subscription_requires_interval() -> None:
    with pytest.raises(ValidationError):
        SubscriptionCommand(
            type="subscribe",
            channel="candles",
            instrument_id="BTC-USDT",
        )


def test_quote_subscription_rejects_interval() -> None:
    with pytest.raises(ValidationError):
        SubscriptionCommand(
            type="subscribe",
            channel="quotes",
            instrument_id="BTC-USDT",
            interval="1m",
        )


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        SubscriptionCommand(
            type="subscribe",
            channel="quotes",
            instrument_id="BTC-USDT",
            something_random=True,
        )