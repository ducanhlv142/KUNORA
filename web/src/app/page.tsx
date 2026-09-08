import { CandlestickChart } from "@/components/market/CandlestickChart";
import {
  getCandles,
  getQuote,
} from "@/lib/api/market";

export default async function Home() {
  const [quote, candles] = await Promise.all([
    getQuote("BTC-USDT"),
    getCandles("BTC-USDT", "1h", 200),
  ]);

  const price = Number(quote.last);
  const change = Number(quote.change_percent_24h ?? 0);

  return (
    <main className="min-h-screen bg-black p-10 text-white">
      <div className="mx-auto max-w-6xl">
        <p className="text-sm text-zinc-500">
          KUNORA / MARKET
        </p>

        <h1 className="mt-2 text-4xl font-semibold">
          BTC / USDT
        </h1>

        <div className="mt-10">
          <p className="text-5xl font-semibold tracking-tight">
            {price.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>

          <p className="mt-3 text-lg">
            {change >= 0 ? "+" : ""}
            {change.toFixed(3)}%
          </p>
        </div>

        <div className="mt-12 grid grid-cols-3 gap-4">
          <MarketStat
            label="24H HIGH"
            value={quote.high_24h}
          />

          <MarketStat
            label="24H LOW"
            value={quote.low_24h}
          />

          <MarketStat
            label="24H VOLUME"
            value={quote.base_volume_24h}
          />
        </div>
        <div className="mt-10">
          <CandlestickChart candles={candles} />
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
  value: string | null;
}) {
  return (
    <div className="rounded-xl border border-zinc-800 p-5">
      <p className="text-xs text-zinc-500">
        {label}
      </p>

      <p className="mt-2 text-xl">
        {value ?? "—"}
      </p>
    </div>
  );
}