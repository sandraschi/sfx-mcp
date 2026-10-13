import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

export default function Dashboard() {
  const [health, setHealth] = useState<{ has_api_key: boolean; version: string } | null>(null);
  const [localCount, setLocalCount] = useState(0);
  const [error, setError] = useState("");

  const refresh = useCallback(() => {
    api
      .health()
      .then((h) => setHealth({ has_api_key: h.has_api_key, version: h.version }))
      .catch((e: Error) => setError(e.message));
    api
      .local()
      .then((d) => setLocalCount(d.total))
      .catch(() => {});
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div>
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-6">
        <h1 className="text-2xl font-bold" data-testid="dashboard-hero">
          sfx-mcp
        </h1>
        <p className="mt-1 text-sm text-zinc-400">
          CC0 sound effects from FreeSound: search, download, keep a local library.
        </p>
        <Link
          to="/sounds"
          className="mt-4 inline-block rounded bg-amber-500 px-4 py-2 text-sm font-semibold text-black hover:bg-amber-400"
          data-testid="dashboard-cta"
        >
          Search sounds
        </Link>
      </div>
      {error && <p className="mt-4 text-sm text-red-400">Backend error: {error}</p>}
      <div className="mt-4 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4" data-testid="kpi-key">
          <div className="text-3xl font-bold">{health ? (health.has_api_key ? "Yes" : "No") : "-"}</div>
          <div className="text-sm text-zinc-400">API key</div>
        </div>
        <Link
          to="/library"
          className="rounded-lg border border-zinc-800 bg-zinc-900 p-4 hover:border-zinc-600"
          data-testid="kpi-library"
        >
          <div className="text-3xl font-bold">{localCount}</div>
          <div className="text-sm text-zinc-400">Cached sounds</div>
        </Link>
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4" data-testid="kpi-version">
          <div className="text-3xl font-bold">{health ? health.version : "-"}</div>
          <div className="text-sm text-zinc-400">Version</div>
        </div>
      </div>
      {health && !health.has_api_key && (
        <p
          className="mt-4 rounded border border-amber-900 bg-amber-950 p-3 text-sm text-amber-300"
          data-testid="dashboard-nokey"
        >
          No FreeSound API key configured. Set FREESOUND_API_KEY in .env — search and download stay disabled until then.
          Your local library below still works.
        </p>
      )}
    </div>
  );
}
