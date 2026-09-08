"use client";

import { useEffect, useRef } from "react";
import {
  CandlestickSeries,
  ColorType,
  createChart,
  type UTCTimestamp,
} from "lightweight-charts";

import type { Candle } from "@/lib/api/market";

interface CandlestickChartProps {
  candles: Candle[];
}

export function CandlestickChart({
  candles,
}: CandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    const chart = createChart(container, {
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
    });

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
      candles.map((candle) => ({
        time: (
          new Date(candle.open_time).getTime() / 1000
        ) as UTCTimestamp,

        open: Number(candle.open),
        high: Number(candle.high),
        low: Number(candle.low),
        close: Number(candle.close),
      })),
    );

    chart.timeScale().fitContent();

    const observer = new ResizeObserver(() => {
      chart.applyOptions({
        width: container.clientWidth,
      });
    });

    observer.observe(container);

    return () => {
      observer.disconnect();
      chart.remove();
    };
  }, [candles]);

  return (
    <div
      ref={containerRef}
      className="w-full overflow-hidden rounded-xl border border-zinc-800"
    />
  );
}