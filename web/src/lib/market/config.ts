export const MARKET_INSTRUMENTS = [
  {
    id: "BTC-USDT",
    label: "BTC / USDT",
  },
  {
    id: "ETH-USDT",
    label: "ETH / USDT",
  },
] as const;

export const MARKET_INTERVALS = [
  "1m",
  "5m",
  "15m",
  "1h",
  "4h",
  "1d",
] as const;

export type MarketInstrumentId =
  (typeof MARKET_INSTRUMENTS)[number]["id"];

export type MarketInterval =
  (typeof MARKET_INTERVALS)[number];

export const DEFAULT_INSTRUMENT: MarketInstrumentId =
  "BTC-USDT";

export const DEFAULT_INTERVAL: MarketInterval =
  "1h";