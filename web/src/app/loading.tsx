export default function Loading() {
  return (
    <main className="min-h-screen bg-black p-10 text-white">
      <div className="mx-auto max-w-6xl animate-pulse">
        <div className="flex items-start justify-between gap-6">
          <div>
            <div className="h-4 w-32 rounded bg-zinc-900" />
            <div className="mt-3 h-10 w-56 rounded bg-zinc-900" />
          </div>

          <div className="h-10 w-80 rounded bg-zinc-900" />
        </div>

        <div className="mt-10">
          <div className="h-14 w-64 rounded bg-zinc-900" />
          <div className="mt-3 h-6 w-24 rounded bg-zinc-900" />
        </div>

        <div className="mt-12 grid gap-4 md:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div
              key={index}
              className="h-24 rounded-xl border border-zinc-900 bg-zinc-950"
            />
          ))}
        </div>

        <div className="mt-10 h-[460px] rounded-xl border border-zinc-900 bg-zinc-950" />
      </div>
    </main>
  );
}