import asyncio

from app.domain.market import CandleInterval
from app.providers.binance.provider import BinanceMarketDataProvider

async def main() -> None:
    async with BinanceMarketDataProvider() as provider:
        instrument = await provider.get_instrument("BTC-USDT")
        quote = await provider.get_quote("BTC-USDT")
        candles = await provider.get_candles(
            "BTC-USDT", 
            CandleInterval.ONE_HOUR, 
            limit=3,
        )

        print("=== Instrument ===")
        print(instrument.model_dump_json(indent=2))

        print("\n=== Quote ===")
        print(quote.model_dump_json(indent=2))

        print("\n=== Candles ===")
        for candle in candles:
            print(candle.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())