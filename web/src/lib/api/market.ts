const API_URL =
  process.env.KUNORA_API_URL ?? "http://127.0.0.1:8000";

export interface Quote {
  instrument_id: string;

  bid: string | null;
  ask: string | null;
  last: string;

  open_24h: string | null;
  high_24h: string | null;
  low_24h: string | null;

  price_change_24h: string | null;
  change_percent_24h: string | null;

  base_volume_24h: string | null;
  quote_volume_24h: string | null;

  timestamp: string;
  source: string;
}

export async function getQuote(
  instrumentId: string,
): Promise<Quote> {
  const response = await fetch(
    `${API_URL}/api/v1/market/quotes/${instrumentId}`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Kunora API returned ${response.status}`,
    );
  }

  return response.json();
}