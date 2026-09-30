"use client";

import { useEffect, useRef } from "react";
import {
  CandlestickSeries,
  ColorType,
  createChart,
  type UTCTimestamp,
} from "lightweight-charts";

import {
  useCandleStream,
  type RealtimeStatus,
} from "@/hooks/useCandleStream";
import type { Candle } from "@/lib/api/market";


interface CandlestickChartProps {
  candles: Candle[];
  instrumentId: string;
  interval: string;
}


function toChartCandle(candle: Candle) {
  return {
    time: (
      new Date(candle.open_time).getTime() / 1000
    ) as UTCTimestamp,

    open: Number(candle.open),
    high: Number(candle.high),
    low: Number(candle.low),
    close: Number(candle.close),
  };
}


export function CandlestickChart({
  candles,
  instrumentId,
  interval,
}: CandlestickChartProps) {
  const containerRef =
    useRef<HTMLDivElement>(null);

  const updateCandleRef =
    useRef<(candle: Candle) => void>(
      () => {},
    );

  useEffect(() => {
    const container =
      containerRef.current;

    if (!container) {
      return;
    }

    const chart = createChart(
      container,
      {
        width: container.clientWidth,
        height: 460,

        layout: {
          background: {
            type: ColorType.Solid,
            color: "#000000",
          },
          textColor: "#a1a1aa",
        },

        grid: {
          vertLines: {
            color: "#18181b",
          },
          horzLines: {
            color: "#18181b",
          },
        },

        rightPriceScale: {
          borderColor: "#27272a",
        },

        timeScale: {
          borderColor: "#27272a",
          timeVisible: true,
        },
      },
    );

    const series = chart.addSeries(
      CandlestickSeries,
      {
        upColor: "#22c55e",
        downColor: "#ef4444",

        wickUpColor: "#22c55e",
        wickDownColor: "#ef4444",

        borderVisible: false,
      },
    );

    series.setData(
      candles.map(toChartCandle),
    );

    updateCandleRef.current = (
      candle: Candle,
    ) => {
      series.update(
        toChartCandle(candle),
      );
    };

    chart.timeScale().fitContent();

    const observer =
      new ResizeObserver(() => {
        chart.applyOptions({
          width: container.clientWidth,
        });
      });

    observer.observe(container);

    return () => {
      updateCandleRef.current = () => {};

      observer.disconnect();
      chart.remove();
    };
  }, [candles]);

  const realtimeStatus =
    useCandleStream({
      instrumentId,
      interval,

      onCandle: (candle) => {
        updateCandleRef.current(
          candle,
        );
      },
    });

  return (
    <div className="relative">
      <div className="absolute right-3 top-3 z-10">
        <RealtimeBadge
          status={realtimeStatus}
        />
      </div>

      <div
        ref={containerRef}
        className="w-full overflow-hidden rounded-xl border border-zinc-800"
      />
    </div>
  );
}


function RealtimeBadge({
  status,
}: {
  status: RealtimeStatus;
}) {
  const config = {
    connecting: {
      label: "CONNECTING",
      dot: "bg-amber-400",
    },

    live: {
      label: "LIVE",
      dot: "bg-emerald-500",
    },

    reconnecting: {
      label: "RECONNECTING",
      dot: "bg-amber-400",
    },

    offline: {
      label: "OFFLINE",
      dot: "bg-red-500",
    },
  } satisfies Record<
    RealtimeStatus,
    {
      label: string;
      dot: string;
    }
  >;

  const current = config[status];

  return (
    <div className="flex items-center gap-2 rounded-md border border-zinc-800 bg-black/80 px-3 py-1.5 text-xs font-medium text-zinc-300 backdrop-blur">
      <span
        className={`h-2 w-2 rounded-full ${current.dot}`}
      />

      {current.label}
    </div>
  );
}