import asyncio
import logging
from contextlib import suppress
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import ValidationError

from app.api.dependencies import (
    get_market_stream_service,
)
from app.api.ws.models import (
    StreamChannel,
    SubscriptionAction,
    SubscriptionCommand,
)
from app.domain.market import CandleInterval
from app.domain.market.exceptions import (
    InstrumentNotFoundError,
    MarketDataUnavailableError,
    MarketError,
)
from app.services.market_stream import (
    MarketStreamService,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
)

StreamService = Annotated[
    MarketStreamService,
    Depends(get_market_stream_service),
]

SubscriptionKey = tuple[
    StreamChannel,
    str,
    CandleInterval | None,
]


@router.websocket("/market")
async def market_stream(
    websocket: WebSocket,
    service: StreamService,
) -> None:
    await websocket.accept()

    send_lock = asyncio.Lock()

    subscriptions: dict[
        SubscriptionKey,
        asyncio.Task[None],
    ] = {}

    async def send_json(
        payload: dict,
    ) -> None:
        async with send_lock:
            await websocket.send_json(payload)

    async def send_error(
        code: str,
        message: str,
    ) -> None:
        await send_json(
            {
                "type": "error",
                "error": {
                    "code": code,
                    "message": message,
                },
            }
        )

    async def forward_candles(
        key: SubscriptionKey,
        instrument_id: str,
        interval: CandleInterval,
    ) -> None:
        try:
            async for candle in service.stream_candles(
                [instrument_id],
                interval,
            ):
                await send_json(
                    {
                        "type": "candle",
                        "channel": "candles",
                        "instrument_id": instrument_id,
                        "interval": interval.value,
                        "data": candle.model_dump(
                            mode="json"
                        ),
                    }
                )

        except asyncio.CancelledError:
            raise

        except InstrumentNotFoundError as exc:
            await send_error(
                "INSTRUMENT_NOT_FOUND",
                str(exc),
            )

        except MarketDataUnavailableError as exc:
            await send_error(
                "MARKET_DATA_UNAVAILABLE",
                str(exc),
            )

        except MarketError as exc:
            await send_error(
                "MARKET_STREAM_ERROR",
                str(exc),
            )

        except Exception:
            logger.exception(
                "Unexpected candle stream failure"
            )

            with suppress(Exception):
                await send_error(
                    "INTERNAL_STREAM_ERROR",
                    "Unexpected market stream failure.",
                )

        finally:
            subscriptions.pop(
                key,
                None,
            )

    async def forward_quotes(
        key: SubscriptionKey,
        instrument_id: str,
    ) -> None:
        try:
            async for quote in service.stream_quotes(
                [instrument_id]
            ):
                await send_json(
                    {
                        "type": "quote",
                        "channel": "quotes",
                        "instrument_id": instrument_id,
                        "data": quote.model_dump(
                            mode="json"
                        ),
                    }
                )

        except asyncio.CancelledError:
            raise

        except InstrumentNotFoundError as exc:
            await send_error(
                "INSTRUMENT_NOT_FOUND",
                str(exc),
            )

        except MarketDataUnavailableError as exc:
            await send_error(
                "MARKET_DATA_UNAVAILABLE",
                str(exc),
            )

        except MarketError as exc:
            await send_error(
                "MARKET_STREAM_ERROR",
                str(exc),
            )

        except Exception:
            logger.exception(
                "Unexpected quote stream failure"
            )

            with suppress(Exception):
                await send_error(
                    "INTERNAL_STREAM_ERROR",
                    "Unexpected market stream failure.",
                )

        finally:
            subscriptions.pop(
                key,
                None,
            )

    async def stop_subscription(
        key: SubscriptionKey,
    ) -> None:
        task = subscriptions.pop(
            key,
            None,
        )

        if task is None:
            return

        task.cancel()

        with suppress(
            asyncio.CancelledError
        ):
            await task

    try:
        while True:
            try:
                payload = (
                    await websocket.receive_json()
                )

                command = (
                    SubscriptionCommand
                    .model_validate(payload)
                )

            except ValidationError as exc:
                await send_error(
                    "INVALID_SUBSCRIPTION",
                    exc.errors()[0]["msg"],
                )
                continue

            if (
                command.channel
                is StreamChannel.TRADES
            ):
                await send_error(
                    "CHANNEL_NOT_SUPPORTED",
                    "Channel 'trades' is not supported yet.",
                )
                continue

            if (
                command.channel
                is StreamChannel.CANDLES
            ):
                interval = command.interval

                if interval is None:
                    await send_error(
                        "INVALID_SUBSCRIPTION",
                        "Candle interval is required.",
                    )
                    continue

                key: SubscriptionKey = (
                    StreamChannel.CANDLES,
                    command.instrument_id,
                    interval,
                )

                if (
                    command.type
                    is SubscriptionAction.SUBSCRIBE
                ):
                    if key in subscriptions:
                        continue

                    await send_json(
                        {
                            "type": "subscribed",
                            "channel": "candles",
                            "instrument_id": (
                                command.instrument_id
                            ),
                            "interval": interval.value,
                        }
                    )

                    subscriptions[key] = (
                        asyncio.create_task(
                            forward_candles(
                                key,
                                command.instrument_id,
                                interval,
                            )
                        )
                    )

                else:
                    await stop_subscription(
                        key
                    )

                    await send_json(
                        {
                            "type": "unsubscribed",
                            "channel": "candles",
                            "instrument_id": (
                                command.instrument_id
                            ),
                            "interval": interval.value,
                        }
                    )

                continue

            if (
                command.channel
                is StreamChannel.QUOTES
            ):
                key = (
                    StreamChannel.QUOTES,
                    command.instrument_id,
                    None,
                )

                if (
                    command.type
                    is SubscriptionAction.SUBSCRIBE
                ):
                    if key in subscriptions:
                        continue

                    await send_json(
                        {
                            "type": "subscribed",
                            "channel": "quotes",
                            "instrument_id": (
                                command.instrument_id
                            ),
                        }
                    )

                    subscriptions[key] = (
                        asyncio.create_task(
                            forward_quotes(
                                key,
                                command.instrument_id,
                            )
                        )
                    )

                else:
                    await stop_subscription(
                        key
                    )

                    await send_json(
                        {
                            "type": "unsubscribed",
                            "channel": "quotes",
                            "instrument_id": (
                                command.instrument_id
                            ),
                        }
                    )

    except WebSocketDisconnect:
        pass

    finally:
        tasks = list(
            subscriptions.values()
        )

        subscriptions.clear()

        for task in tasks:
            task.cancel()

        for task in tasks:
            with suppress(
                asyncio.CancelledError
            ):
                await task