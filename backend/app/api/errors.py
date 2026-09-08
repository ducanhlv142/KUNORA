from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.market.exceptions import (
    InstrumentNotFoundError,
    MarketDataUnavailableError,
)


def register_exception_handlers(
    app: FastAPI,
) -> None:
    @app.exception_handler(InstrumentNotFoundError)
    async def instrument_not_found_handler(
        request: Request,
        exc: InstrumentNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "INSTRUMENT_NOT_FOUND",
                    "message": str(exc),
                }
            },
        )

    @app.exception_handler(MarketDataUnavailableError)
    async def market_data_unavailable_handler(
        request: Request,
        exc: MarketDataUnavailableError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "MARKET_DATA_UNAVAILABLE",
                    "message": str(exc),
                }
            },
        )