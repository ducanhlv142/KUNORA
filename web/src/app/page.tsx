import { CandlestickChart } from "@/components/market/CandlestickChart";
import { MarketControls } from "@/components/market/MarketControls";
import {
  getCandles,
  getQuote,
} from "@/lib/api/market";
import {
  formatPercent,
  formatPrice,
  formatVolume,
} from "@/lib/format/market";


const SUPPORTED_INSTRUMENTS = [
  "BTC-USDT",
  "ETH-USDT",
] as const;

const SUPPORTED_INTERVALS = [
  "1m",
  "5m",
  "15m",
  "1h",
  "4h",
  "1d",
] as const;


type SearchParams = {
  instrument?: string;
  interval?: string;
};


function resolveInstrument(
  value: string | undefined,
): string {
  if (
    value &&
    SUPPORTED_INSTRUMENTS.includes(
      value as (typeof SUPPORTED_INSTRUMENTS)[number],
    )
  ) {
    return value;
  }

  return "BTC-USDT";
}


function resolveInterval(
  value: string | undefined,
): string {
  if (
    value &&
    SUPPORTED_INTERVALS.includes(
      value as (typeof SUPPORTED_INTERVALS)[number],
    )
  ) {
    return value;
  }

  return "1h";
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

  const [quote, candles] = await Promise.all([
    getQuote(instrument),
    getCandles(
      instrument,
      interval,
      200,
    ),
  ]);

  const change = Number(
    quote.change_percent_24h ?? 0,
  );

  const instrumentLabel = instrument.replace(
    "-",
    " / ",
  );

  return (
    <main className="min-h-screen bg-black p-10 text-white">
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

        <div className="mt-10">
          <p className="text-5xl font-semibold tracking-tight">
            {formatPrice(quote.last)}
          </p>

          <p
            className={[
              "mt-3 text-lg font-medium",
              change > 0
                ? "text-emerald-500"
                : change < 0
                  ? "text-red-500"
                  : "text-zinc-400",
            ].join(" ")}
          >
            {formatPercent(
              quote.change_percent_24h,
            )}
          </p>
        </div>

        <div className="mt-12 grid gap-4 md:grid-cols-3">
          <MarketStat
            label="24H HIGH"
            value={formatPrice(
              quote.high_24h,
            )}
          />

          <MarketStat
            label="24H LOW"
            value={formatPrice(
              quote.low_24h,
            )}
          />

          <MarketStat
            label="24H VOLUME"
            value={`${formatVolume(
              quote.base_volume_24h,
            )} ${instrument.split("-")[0]}`}
          />
        </div>

        <div className="mt-10">
          <CandlestickChart
            candles={candles}
          />
        </div>
      </div>
    </main>
  );
}


function MarketStat({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-800 p-5">
      <p className="text-xs text-zinc-500">
        {label}
      </p>

      <p className="mt-2 text-xl font-medium">
        {value}
      </p>
    </div>
  );
}