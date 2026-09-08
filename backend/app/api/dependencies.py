from fastapi import Request

from app.services.market_data import MarketDataService


def get_market_data_service(
    request: Request,
) -> MarketDataService:
    return request.app.state.market_data_service