import { Download, Search } from "lucide-react";
import { useState } from "react";
import { type Sound, api } from "../lib/api";

export default function Sounds() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<Sound[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [downloaded, setDownloaded] = useState<Record<number, string>>({});

  const search = () => {
    if (!q.trim()) return;
    setBusy(true);
    setError("");
    api
      .search(q)
      .then((d) => {
        setResults(d.results);
        setTotal(d.total);
      })
      .catch((e: Error) => {
        setError(e.message);
        setResults([]);
      })
      .finally(() => setBusy(false));
  };

  const download = (id: number) => {
    setDownloaded((d) => ({ ...d, [id]: "…" }));
    api
      .download(id)
      .then(() => setDownloaded((d) => ({ ...d, [id]: "saved" })))
      .catch((e: Error) => setDownloaded((d) => ({ ...d, [id]: `failed: ${e.message}` })));
  };

  return (
    <div>
      <h1 className="text-xl font-bold" data-testid="sounds-title">
        Sounds
      </h1>
      <div className="mt-4 flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") search();
          }}
          placeholder="thunder, footsteps, ui click…"
          className="w-full max-w-md rounded border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm"
          data-testid="sounds-query"
        />
        <button
          type="button"
          onClick={search}
          disabled={busy || !q.trim()}
          className="flex items-center gap-1 rounded bg-amber-500 px-3 py-2 text-sm font-semibold text-black disabled:opacity-40"
          data-testid="sounds-search"
        >
          <Search size={16} /> {busy ? "…" : "Search"}
        </button>
      </div>
      {error && (
        <p
          className="mt-4 rounded border border-amber-900 bg-amber-950 p-3 text-sm text-amber-300"
          data-testid="sounds-error"
        >
          Search unavailable: {error}. FreeSound search needs FREESOUND_API_KEY in .env.
        </p>
      )}
      {results.length > 0 && (
        <p className="mt-3 text-xs text-zinc-500" data-testid="sounds-count">
          {total} results
        </p>
      )}
      <ul className="mt-2 space-y-2" data-testid="sounds-list">
        {results.map((s) => (
          <li key={s.id} className="rounded border border-zinc-800 bg-zinc-900 px-4 py-3">
            <div className="flex items-center justify-between gap-2">
              <div className="text-sm font-semibold">{s.name}</div>
              <button
                type="button"
                onClick={() => download(s.id)}
                className="flex shrink-0 items-center gap-1 rounded border border-zinc-700 px-2 py-1 text-xs hover:bg-zinc-800"
                data-testid={`sounds-dl-${s.id}`}
              >
                <Download size={14} /> {downloaded[s.id] ?? "Cache"}
              </button>
            </div>
            <div className="mt-1 text-xs text-zinc-500">
              {s.duration.toFixed(1)}s · {s.license} · {(s.tags || []).slice(0, 5).join(", ")}
            </div>
            {s.preview_url && (
              <audio
                controls
                preload="none"
                src={s.preview_url}
                className="mt-2 w-full"
                data-testid={`sounds-audio-${s.id}`}
              />
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
