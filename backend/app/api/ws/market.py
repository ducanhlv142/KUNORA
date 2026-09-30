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
from app.domain.market import (
    CandleInterval,
)
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


@router.websocket("/market")
async def market_stream(
    websocket: WebSocket,
    service: StreamService,
) -> None:
    await websocket.accept()

    send_lock = asyncio.Lock()

    subscriptions: dict[
        tuple[str, CandleInterval],
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
        key: tuple[str, CandleInterval],
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
                "Unexpected market stream failure"
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
        key: tuple[str, CandleInterval],
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
                is not StreamChannel.CANDLES
            ):
                await send_error(
                    "CHANNEL_NOT_SUPPORTED",
                    (
                        f"Channel "
                        f"'{command.channel.value}' "
                        f"is not supported yet."
                    ),
                )
                continue

            interval = command.interval

            if interval is None:
                await send_error(
                    "INVALID_SUBSCRIPTION",
                    "Candle interval is required.",
                )
                continue

            key = (
                command.instrument_id,
                interval,
            )

            if (
                command.type
                is SubscriptionAction.SUBSCRIBE
            ):
                if key in subscriptions:
                    continue

                # Acknowledge first so the client
                # always sees protocol state before
                # the first market event.
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

            elif (
                command.type
                is SubscriptionAction.UNSUBSCRIBE
            ):
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