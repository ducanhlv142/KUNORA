"use client";

import {
  usePathname,
  useRouter,
  useSearchParams,
} from "next/navigation";
import { useTransition } from "react";

import {
  MARKET_INSTRUMENTS,
  MARKET_INTERVALS,
} from "@/lib/market/config";

interface MarketControlsProps {
  instrument: string;
  interval: string;
}


export function MarketControls({
  instrument,
  interval,
}: MarketControlsProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [isPending, startTransition] = useTransition();

  function updateMarket(
    key: "instrument" | "interval",
    value: string,
  ) {
    const params = new URLSearchParams(
      searchParams.toString(),
    );

    params.set(key, value);

    startTransition(() => {
      router.push(
        `${pathname}?${params.toString()}`,
      );
    });
  }

  return (
    <div
      className={[
        "flex flex-wrap items-center gap-3",
        isPending ? "opacity-60" : "",
      ].join(" ")}
    >
      <select
        value={instrument}
        onChange={(event) =>
          updateMarket(
            "instrument",
            event.target.value,
          )
        }
        disabled={isPending}
        className="rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-200 outline-none"
      >
        {MARKET_INSTRUMENTS.map((item) => (
          <option
            key={item.id}
            value={item.id}
          >
            {item.label}
          </option>
        ))}
      </select>

      <div className="flex gap-1">
        {MARKET_INTERVALS.map((item) => {
          const active = item === interval;

          return (
            <button
              key={item}
              type="button"
              disabled={isPending}
              onClick={() =>
                updateMarket(
                  "interval",
                  item,
                )
              }
              className={[
                "rounded-md px-3 py-2 text-xs",
                "transition-colors",
                active
                  ? "bg-white text-black"
                  : [
                      "text-zinc-400",
                      "hover:bg-zinc-900",
                      "hover:text-white",
                    ].join(" "),
              ].join(" ")}
            >
              {item}
            </button>
          );
        })}
      </div>
    </div>
  );
}