export function AppHeader() {
  return (
    <header className="flex h-14 items-center border-b border-zinc-900 bg-black px-5">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-zinc-800 bg-zinc-950 text-sm font-semibold">
          K
        </div>

        <div>
          <p className="text-sm font-semibold tracking-[0.18em] text-white">
            KUNORA
          </p>

          <p className="text-[10px] text-zinc-600">
            MARKET INTELLIGENCE
          </p>
        </div>
      </div>

      <div className="ml-auto flex items-center gap-3">
        <span className="rounded-md border border-zinc-800 px-2 py-1 text-[10px] text-zinc-500">
          v0.1
        </span>
      </div>
    </header>
  );
}