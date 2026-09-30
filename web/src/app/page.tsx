import { CandlestickChart } from "@/components/market/CandlestickChart";
import { MarketControls } from "@/components/market/MarketControls";
import { MarketUnavailable } from "@/components/market/MarketUnavailable";
import { LiveQuotePanel } from "@/components/market/LiveQuotePanel";

import {
  getCandles,
  getQuote,
} from "@/lib/api/market";
import type {
  Candle,
  Quote,
} from "@/lib/api/market";

import {
  DEFAULT_INSTRUMENT,
  DEFAULT_INTERVAL,
  MARKET_INSTRUMENTS,
  MARKET_INTERVALS,
  type MarketInstrumentId,
  type MarketInterval,
} from "@/lib/market/config";

type SearchParams = {
  instrument?: string;
  interval?: string;
};


function resolveInstrument(
  value: string | undefined,
): MarketInstrumentId {
  if (
    value &&
    MARKET_INSTRUMENTS.some(
      (instrument) =>
        instrument.id === value,
    )
  ) {
    return value as MarketInstrumentId;
  }

  return DEFAULT_INSTRUMENT;
}

function resolveInterval(
  value: string | undefined,
): MarketInterval {
  if (
    value &&
    MARKET_INTERVALS.includes(
      value as MarketInterval,
    )
  ) {
    return value as MarketInterval;
  }

  return DEFAULT_INTERVAL;
}

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;

  const instrument = resolveInstrument(
    params.instrument,
  );

  const interval = resolveInterval(
    params.interval,
  );

  let quote: Quote;
  let candles: Candle[];

  try {
    [quote, candles] = await Promise.all([
      getQuote(instrument),
      getCandles(
        instrument,
        interval,
        200,
      ),
    ]);
  } catch {
    return <MarketUnavailable />;
  }

  const instrumentLabel = instrument.replace(
    "-",
    " / ",
  );

  return (
    <main className="p-6 md:p-10">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="text-sm text-zinc-500">
              KUNORA / MARKET
            </p>

            <h1 className="mt-2 text-4xl font-semibold">
              {instrumentLabel}
            </h1>
          </div>

          <MarketControls
            instrument={instrument}
            interval={interval}
          />       
        </div>
        <LiveQuotePanel
          initialQuote={quote}
          instrumentId={instrument}
        />
        <div className="mt-10">
          <CandlestickChart
            candles={candles}
            instrumentId={instrument}
            interval={interval}
          />
        </div>
      </div>
    </main>
  );
}
