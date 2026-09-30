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
  instrumentId: string;
  interval: string;
}

interface CandleStreamMessage {
  type: "candle";
  channel: "candles";
  instrument_id: string;
  interval: string;
  data: Candle;
}

const WS_URL =
  process.env.NEXT_PUBLIC_KUNORA_WS_URL ??
  "ws://127.0.0.1:8000/api/v1/ws/market";

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
      candles.map(toChartCandle),
    );

    chart.timeScale().fitContent();

    const observer = new ResizeObserver(() => {
      chart.applyOptions({
        width: container.clientWidth,
      });
    });

    observer.observe(container);

    const websocket = new WebSocket(
      WS_URL,
    );

    websocket.addEventListener(
      "open",
      () => {
        websocket.send(
          JSON.stringify({
            type: "subscribe",
            channel: "candles",
            instrument_id: instrumentId,
            interval,
          }),
        );
      },
    );

    websocket.addEventListener(
      "message",
      (event) => {
        try {
          const message = JSON.parse(
            event.data,
          ) as {
            type?: string;
            channel?: string;
            instrument_id?: string;
            interval?: string;
            data?: Candle;
          };

          if (
            message.type !== "candle" ||
            message.channel !== "candles" ||
            message.instrument_id !==
              instrumentId ||
            message.interval !== interval ||
            !message.data
          ) {
            return;
          }

          const candleMessage =
            message as CandleStreamMessage;

          series.update(
            toChartCandle(
              candleMessage.data,
            ),
          );
        } catch {
          // Ignore malformed realtime messages.
        }
      },
    );

    return () => {
      observer.disconnect();

      if (
        websocket.readyState ===
        WebSocket.OPEN
      ) {
        websocket.send(
          JSON.stringify({
            type: "unsubscribe",
            channel: "candles",
            instrument_id: instrumentId,
            interval,
          }),
        );
      }

      websocket.close();
      chart.remove();
    };
  }, [
    candles,
    instrumentId,
    interval,
  ]);

  return (
    <div
      ref={containerRef}
      className="w-full overflow-hidden rounded-xl border border-zinc-800"
    />
  );
}