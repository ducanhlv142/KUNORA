"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

interface ErrorPageProps {
  error: Error & {
    digest?: string;
  };
  reset: () => void;
}

export default function ErrorPage({
  error,
  reset,
}: ErrorPageProps) {
  const router = useRouter();

  const [isPending, startTransition] = useTransition();
  const [retryError, setRetryError] = useState<string | null>(
    null,
  );

  async function retry() {
    setRetryError(null);

    try {
      const response = await fetch("/api/health", {
        cache: "no-store",
      });

      if (!response.ok) {
        setRetryError(
          "Backend is still unavailable. Please try again shortly.",
        );
        return;
      }

      startTransition(() => {
        router.refresh();
        reset();
      });
    } catch {
      setRetryError(
        "Unable to reach the Kunora backend.",
      );
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-black p-10 text-white">
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
          {isPending ? "Retrying..." : "Try again"}
        </button>

        {retryError && (
          <p className="mt-4 text-sm text-red-400">
            {retryError}
          </p>
        )}

        {process.env.NODE_ENV === "development" && (
          <p className="mt-5 break-all font-mono text-xs text-zinc-600">
            {error.message}
          </p>
        )}
      </div>
    </main>
  );
}