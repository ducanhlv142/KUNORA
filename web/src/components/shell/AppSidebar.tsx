export function AppSidebar() {
  return (
    <aside className="hidden w-52 shrink-0 border-r border-zinc-900 bg-black md:block">
      <nav className="p-3">
        <div className="rounded-lg bg-zinc-900 px-3 py-2.5">
          <p className="text-sm font-medium text-white">
            Markets
          </p>

          <p className="mt-0.5 text-xs text-zinc-500">
            Live market data
          </p>
        </div>

        <div className="mt-2 px-3 py-2.5 opacity-40">
          <p className="text-sm text-zinc-400">
            Watchlist
          </p>

          <p className="mt-0.5 text-[10px] uppercase tracking-wider text-zinc-600">
            Coming soon
          </p>
        </div>

        <div className="px-3 py-2.5 opacity-40">
          <p className="text-sm text-zinc-400">
            Screener
          </p>

          <p className="mt-0.5 text-[10px] uppercase tracking-wider text-zinc-600">
            Coming soon
          </p>
        </div>
      </nav>
    </aside>
  );
}