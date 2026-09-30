import asyncio
import json

from websockets.asyncio.client import connect


URI = "ws://127.0.0.1:8000/api/v1/ws/market"


async def main() -> None:
    async with connect(URI) as websocket:
        subscribe = {
            "type": "subscribe",
            "channel": "candles",
            "instrument_id": "BTC-USDT",
            "interval": "1m",
        }

        await websocket.send(
            json.dumps(subscribe)
        )

        candle_count = 0

        while candle_count < 3:
            raw = await websocket.recv()
            message = json.loads(raw)

            print(
                json.dumps(
                    message,
                    indent=2,
                )
            )

            if message.get("type") == "candle":
                candle_count += 1

        unsubscribe = {
            "type": "unsubscribe",
            "channel": "candles",
            "instrument_id": "BTC-USDT",
            "interval": "1m",
        }

        await websocket.send(
            json.dumps(unsubscribe)
        )

        while True:
            raw = await websocket.recv()
            message = json.loads(raw)

            print(
                json.dumps(
                    message,
                    indent=2,
                )
            )

            if message.get("type") == "unsubscribed":
                break


if __name__ == "__main__":
    asyncio.run(main())