"use client";

import {
  useEffect,
  useRef,
} from "react";

import type { Quote } from "@/lib/api/market";


interface UseQuoteStreamOptions {
  instrumentId: string;
  onQuote: (quote: Quote) => void;
}


const WS_URL =
  process.env.NEXT_PUBLIC_KUNORA_WS_URL ??
  "ws://127.0.0.1:8000/api/v1/ws/market";


export function useQuoteStream({
  instrumentId,
  onQuote,
}: UseQuoteStreamOptions): void {
  const onQuoteRef = useRef(onQuote);

  useEffect(() => {
    onQuoteRef.current = onQuote;
  }, [onQuote]);

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
        return;
      }

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
      if (
        disposed ||
        !navigator.onLine
      ) {
        return;
      }

      clearReconnectTimer();

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
              channel: "quotes",
              instrument_id: instrumentId,
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
              data?: Quote;
            };

            if (
              message.type === "subscribed" &&
              message.channel === "quotes" &&
              message.instrument_id ===
                instrumentId
            ) {
              reconnectAttempt = 0;
              return;
            }

            if (
              message.type !== "quote" ||
              message.channel !== "quotes" ||
              message.instrument_id !==
                instrumentId ||
              !message.data
            ) {
              return;
            }

            reconnectAttempt = 0;

            onQuoteRef.current(
              message.data,
            );
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
            channel: "quotes",
            instrument_id: instrumentId,
          }),
        );
      }

      currentSocket?.close();
    };
  }, [instrumentId]);
}