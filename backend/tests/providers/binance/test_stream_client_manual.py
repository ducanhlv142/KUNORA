import asyncio
from contextlib import aclosing

from app.providers.binance.stream_client import (
    BinanceStreamClient,
)


async def main() -> None:
    client = BinanceStreamClient()

    stream_name = client.kline_stream(
        "BTCUSDT",
        "1m",
    )

    count = 0

    async with aclosing(
        client.stream([stream_name])
    ) as messages:
        async for message in messages:
            print(message)

            count += 1

            if count >= 3:
                break


if __name__ == "__main__":
    asyncio.run(main())