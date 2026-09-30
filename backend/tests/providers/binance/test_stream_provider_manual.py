import asyncio
from contextlib import aclosing

from app.domain.market import CandleInterval
from app.providers.binance.provider import (
    BinanceMarketDataProvider,
)
from app.providers.binance.stream_provider import (
    BinanceCandleStreamProvider,
)


async def main() -> None:
    market_provider = BinanceMarketDataProvider()

    stream_provider = BinanceCandleStreamProvider(
        market_data_provider=market_provider,
    )

    try:
        candles = stream_provider.stream_candles(
            ["BTC-USDT"],
            CandleInterval.ONE_MINUTE,
        )

        count = 0

        async with aclosing(candles):
            async for candle in candles:
                print(
                    candle.model_dump_json(
                        indent=2,
                    )
                )

                count += 1

                if count >= 3:
                    break

    finally:
        await market_provider.close()


if __name__ == "__main__":
    asyncio.run(main())