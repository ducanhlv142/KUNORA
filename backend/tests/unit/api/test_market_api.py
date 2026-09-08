from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.api.dependencies import get_market_data_service
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
from app.domain.market.exceptions import (
    InstrumentNotFoundError,
    MarketDataUnavailableError,
)
from app.main import app


BTC = Asset(
    id="BTC",
    symbol="BTC",
    name="Bitcoin",
    asset_class=AssetClass.CRYPTO,
)

USDT = Asset(
    id="USDT",
    symbol="USDT",
    name="Tether",
    asset_class=AssetClass.CRYPTO,
)

INSTRUMENT = Instrument(
    id="BTC-USDT",
    symbol="BTC/USDT",
    base_asset=BTC,
    quote_asset=USDT,
    instrument_type=InstrumentType.SPOT,
    venue="BINANCE",
    status=MarketStatus.ACTIVE,
)

QUOTE = Quote(
    instrument_id="BTC-USDT",
    last=Decimal("80000.12"),
    open_24h=Decimal("79000"),
    high_24h=Decimal("81000"),
    low_24h=Decimal("78500"),
    price_change_24h=Decimal("1000.12"),
    change_percent_24h=Decimal("1.266"),
    base_volume_24h=Decimal("1234.56"),
    quote_volume_24h=Decimal("98765432.10"),
    timestamp=datetime(
        2026,
        9,
        8,
        9,
        0,
        tzinfo=timezone.utc,
    ),
    source="binance",
)

CANDLE = Candle(
    instrument_id="BTC-USDT",
    interval=CandleInterval.ONE_HOUR,
    open_time=datetime(
        2026,
        9,
        8,
        8,
        0,
        tzinfo=timezone.utc,
    ),
    close_time=datetime(
        2026,
        9,
        8,
        8,
        59,
        59,
        999000,
        tzinfo=timezone.utc,
    ),
    open=Decimal("79000"),
    high=Decimal("80500"),
    low=Decimal("78800"),
    close=Decimal("80000"),
    volume=Decimal("100"),
    quote_volume=Decimal("8000000"),
    is_closed=True,
    source="binance",
)


class FakeMarketDataService:
    async def get_instrument(
        self,
        instrument_id: str,
    ) -> Instrument:
        if instrument_id.upper() != "BTC-USDT":
            raise InstrumentNotFoundError(instrument_id)

        return INSTRUMENT

    async def get_quote(
        self,
        instrument_id: str,
    ) -> Quote:
        if instrument_id.upper() != "BTC-USDT":
            raise InstrumentNotFoundError(instrument_id)

        return QUOTE

    async def get_candles(
        self,
        instrument_id: str,
        interval: CandleInterval,
        limit: int,
    ) -> list[Candle]:
        if instrument_id.upper() != "BTC-USDT":
            raise InstrumentNotFoundError(instrument_id)

        return [CANDLE]


class UnavailableMarketDataService(FakeMarketDataService):
    async def get_quote(
        self,
        instrument_id: str,
    ) -> Quote:
        raise MarketDataUnavailableError()


def override_service(service: object) -> None:
    app.dependency_overrides[get_market_data_service] = (
        lambda: service
    )


def clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_get_instrument() -> None:
    override_service(FakeMarketDataService())

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/market/instruments/BTC-USDT"
            )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == "BTC-USDT"
        assert data["base_asset"]["id"] == "BTC"
        assert data["quote_asset"]["id"] == "USDT"

    finally:
        clear_overrides()


def test_get_quote() -> None:
    override_service(FakeMarketDataService())

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/market/quotes/BTC-USDT"
            )

        assert response.status_code == 200

        data = response.json()

        assert data["instrument_id"] == "BTC-USDT"
        assert data["last"] == "80000.12"
        assert data["source"] == "binance"

    finally:
        clear_overrides()


def test_get_candles() -> None:
    override_service(FakeMarketDataService())

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/market/candles/BTC-USDT",
                params={
                    "interval": "1h",
                    "limit": 1,
                },
            )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["interval"] == "1h"
        assert data[0]["is_closed"] is True

    finally:
        clear_overrides()


def test_unknown_instrument_returns_stable_404() -> None:
    override_service(FakeMarketDataService())

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/market/quotes/UNKNOWN-USDT"
            )

        assert response.status_code == 404

        assert response.json() == {
            "error": {
                "code": "INSTRUMENT_NOT_FOUND",
                "message": (
                    "Instrument 'UNKNOWN-USDT' was not found."
                ),
            }
        }

    finally:
        clear_overrides()


def test_market_failure_returns_stable_503() -> None:
    override_service(UnavailableMarketDataService())

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/market/quotes/BTC-USDT"
            )

        assert response.status_code == 503

        assert response.json()["error"]["code"] == (
            "MARKET_DATA_UNAVAILABLE"
        )

    finally:
        clear_overrides()


def test_candle_limit_validation() -> None:
    override_service(FakeMarketDataService())

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/market/candles/BTC-USDT",
                params={
                    "interval": "1h",
                    "limit": 5000,
                },
            )

        assert response.status_code == 422

    finally:
        clear_overrides()