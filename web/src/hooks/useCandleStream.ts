"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import type { Candle } from "@/lib/api/market";


export type RealtimeStatus =
  | "connecting"
  | "live"
  | "reconnecting"
  | "offline";


interface UseCandleStreamOptions {
  instrumentId: string;
  interval: string;
  onCandle: (candle: Candle) => void;
}


const WS_URL =
  process.env.NEXT_PUBLIC_KUNORA_WS_URL ??
  "ws://127.0.0.1:8000/api/v1/ws/market";


export function useCandleStream({
  instrumentId,
  interval,
  onCandle,
}: UseCandleStreamOptions): RealtimeStatus {
  const [status, setStatus] =
    useState<RealtimeStatus>("connecting");

  const onCandleRef = useRef(onCandle);

  useEffect(() => {
    onCandleRef.current = onCandle;
  }, [onCandle]);

  useEffect(() => {
    let socket: WebSocket | null = null;

    let reconnectTimer:
      | ReturnType<typeof setTimeout>
      | null = null;

    let reconnectAttempt = 0;
    let disposed = false;

    const clearReconnectTimer = () => {
      if (reconnectTimer === null) {
        return;
      }

      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    };

    const scheduleReconnect = () => {
      if (disposed) {
        return;
      }

      clearReconnectTimer();

      if (!navigator.onLine) {
        setStatus("offline");
        return;
      }

      setStatus("reconnecting");

      const delay = Math.min(
        1000 * 2 ** reconnectAttempt,
        10_000,
      );

      reconnectAttempt += 1;

      reconnectTimer = setTimeout(
        connect,
        delay,
      );
    };

    const connect = () => {
      if (disposed) {
        return;
      }

      clearReconnectTimer();

      if (!navigator.onLine) {
        setStatus("offline");
        return;
      }

      setStatus(
        reconnectAttempt === 0
          ? "connecting"
          : "reconnecting",
      );

      const websocket =
        new WebSocket(WS_URL);

      socket = websocket;

      websocket.addEventListener(
        "open",
        () => {
          if (
            disposed ||
            socket !== websocket
          ) {
            websocket.close();
            return;
          }

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
          if (
            disposed ||
            socket !== websocket
          ) {
            return;
          }

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

            const matchesSubscription =
              message.channel === "candles" &&
              message.instrument_id ===
                instrumentId &&
              message.interval === interval;

            if (
              message.type === "subscribed" &&
              matchesSubscription
            ) {
              reconnectAttempt = 0;
              setStatus("live");
              return;
            }

            if (
              message.type === "candle" &&
              matchesSubscription &&
              message.data
            ) {
              reconnectAttempt = 0;
              setStatus("live");

              onCandleRef.current(
                message.data,
              );
            }
          } catch {
            // Ignore malformed messages.
          }
        },
      );

      websocket.addEventListener(
        "error",
        () => {
          websocket.close();
        },
      );

      websocket.addEventListener(
        "close",
        () => {
          if (socket !== websocket) {
            return;
          }

          socket = null;

          scheduleReconnect();
        },
      );
    };

    const handleOffline = () => {
      clearReconnectTimer();

      setStatus("offline");

      const currentSocket = socket;
      socket = null;

      currentSocket?.close();
    };

    const handleOnline = () => {
      reconnectAttempt = 0;
      clearReconnectTimer();

      const currentSocket = socket;
      socket = null;

      currentSocket?.close();

      connect();
    };

    window.addEventListener(
      "offline",
      handleOffline,
    );

    window.addEventListener(
      "online",
      handleOnline,
    );

    connect();

    return () => {
      disposed = true;

      clearReconnectTimer();

      window.removeEventListener(
        "offline",
        handleOffline,
      );

      window.removeEventListener(
        "online",
        handleOnline,
      );

      const currentSocket = socket;
      socket = null;

      if (
        currentSocket?.readyState ===
        WebSocket.OPEN
      ) {
        currentSocket.send(
          JSON.stringify({
            type: "unsubscribe",
            channel: "candles",
            instrument_id: instrumentId,
            interval,
          }),
        );
      }

      currentSocket?.close();
    };
  }, [
    instrumentId,
    interval,
  ]);

  return status;
}