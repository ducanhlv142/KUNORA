"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

export function MarketUnavailable() {
  const router = useRouter();

  const [isPending, startTransition] = useTransition();
  const [message, setMessage] = useState<string | null>(null);

  async function retry() {
    setMessage(null);

    try {
      const response = await fetch("/api/health", {
        cache: "no-store",
      });

      if (!response.ok) {
        setMessage(
          "Backend is still unavailable. Please try again shortly.",
        );
        return;
      }

      startTransition(() => {
        router.refresh();
      });
    } catch {
      setMessage(
        "Unable to reach the Kunora backend.",
      );
    }
  }

  return (
    <main className="flex min-h-[calc(100vh-3.5rem)] items-center justify-center p-6">
      <div className="w-full max-w-lg rounded-2xl border border-zinc-800 p-8">
        <p className="text-sm text-zinc-500">
          KUNORA / MARKET
        </p>

        <h1 className="mt-3 text-2xl font-semibold">
          Market data unavailable
        </h1>

        <p className="mt-3 text-sm leading-6 text-zinc-400">
          Kunora couldn&apos;t load the latest market data.
          The data provider or backend may be temporarily unavailable.
        </p>

        <button
          type="button"
          onClick={retry}
          disabled={isPending}
          className="mt-6 rounded-lg bg-white px-4 py-2 text-sm font-medium text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isPending ? "Checking..." : "Try again"}
        </button>

        {message && (
          <p className="mt-4 text-sm text-red-400">
            {message}
          </p>
        )}
      </div>
    </main>
  );
}