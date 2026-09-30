from fastapi import Request, WebSocket

from app.services.market_data import (
    MarketDataService,
)
from app.services.market_stream import (
    MarketStreamService,
)


def get_market_data_service(
    request: Request,
) -> MarketDataService:
    return request.app.state.market_data_service


def get_market_stream_service(
    websocket: WebSocket,
) -> MarketStreamService:
    return (
        websocket.app.state.market_stream_service
    )