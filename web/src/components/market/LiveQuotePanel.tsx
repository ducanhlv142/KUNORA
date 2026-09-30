"use client";

import { useState } from "react";

import { useQuoteStream } from "@/hooks/useQuoteStream";
import type { Quote } from "@/lib/api/market";
import {
  formatPercent,
  formatPrice,
  formatVolume,
} from "@/lib/format/market";


interface LiveQuotePanelProps {
  initialQuote: Quote;
  instrumentId: string;
}


export function LiveQuotePanel({
  initialQuote,
  instrumentId,
}: LiveQuotePanelProps) {
  const [quote, setQuote] =
    useState<Quote>(initialQuote);

  useQuoteStream({
    instrumentId,

    onQuote: (nextQuote) => {
      setQuote(nextQuote);
    },
  });

  const change = Number(
    quote.change_percent_24h ?? 0,
  );

  const baseAsset =
    instrumentId.split("-")[0];

  return (
    <>
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
          )} ${baseAsset}`}
        />
      </div>
    </>
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