import { useCallback, useEffect, useState } from "react";

interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  kind: string;
  detail: string;
  meta: Record<string, unknown>;
}

interface LogsResponse {
  entries: LogEntry[];
  total: number;
  limit: number;
  offset: number;
  max_entries: number;
  sort: string;
}

const LEVELS = ["", "DEBUG", "INFO", "WARNING", "ERROR"];
const PAGE_SIZE = 50;

export default function Logs() {
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [level, setLevel] = useState("");
  const [kind, setKind] = useState("");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("desc");
  const [tail, setTail] = useState(false);
  const [error, setError] = useState("");

  const query = useCallback(
    (tailAfter?: string) => {
      const p = new URLSearchParams({
        limit: String(PAGE_SIZE),
        offset: tailAfter ? "0" : String(offset),
        sort,
      });
      if (level) p.set("level", level);
      if (kind) p.set("kind", kind);
      if (search) p.set("search", search);
      if (tailAfter) p.set("after_id", tailAfter);
      fetch(`/api/logs?${p.toString()}`)
        .then((r) => {
          if (!r.ok) throw new Error(`/api/logs: ${r.status}`);
          return r.json() as Promise<LogsResponse>;
        })
        .then((d) => {
          if (tailAfter) {
            setEntries((prev) => [...d.entries.reverse(), ...prev].slice(0, 500));
            setTotal((t) => t + d.entries.length);
          } else {
            setEntries(d.entries);
            setTotal(d.total);
          }
        })
        .catch((e: Error) => setError(e.message));
    },
    [offset, level, kind, search, sort],
  );

  useEffect(() => {
    if (tail) return;
    query();
  }, [query, tail]);

  useEffect(() => {
    if (!tail) return;
    const t = setInterval(() => {
      setEntries((prev) => {
        const newest = prev.length > 0 ? prev[0].id : undefined;
        query(newest);
        return prev;
      });
    }, 1500);
    return () => clearInterval(t);
  }, [tail, query]);

  const clear = () => {
    if (!window.confirm("Clear the log buffer?")) return;
    fetch("/api/logs", { method: "DELETE" })
      .then(() => {
        setOffset(0);
        query();
      })
      .catch((e: Error) => setError(e.message));
  };

  const exportHref = (format: string) => {
    const p = new URLSearchParams({ format, sort });
    if (level) p.set("level", level);
    if (kind) p.set("kind", kind);
    if (search) p.set("search", search);
    return `/api/logs/export?${p.toString()}`;
  };

  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const page = Math.floor(offset / PAGE_SIZE) + 1;

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold" data-testid="logs-title">
          Logs
        </h1>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setTail((t) => !t)}
            className={`rounded border px-3 py-1 text-sm ${tail ? "border-amber-500 text-amber-400" : "border-zinc-700 hover:bg-zinc-800"}`}
            data-testid="logs-tail"
          >
            {tail ? "Tail: on" : "Tail: off"}
          </button>
          <a
            href={exportHref("json")}
            className="rounded border border-zinc-700 px-3 py-1 text-sm hover:bg-zinc-800"
            data-testid="logs-export-json"
          >
            JSON
          </a>
          <a
            href={exportHref("csv")}
            className="rounded border border-zinc-700 px-3 py-1 text-sm hover:bg-zinc-800"
            data-testid="logs-export-csv"
          >
            CSV
          </a>
          <button
            type="button"
            onClick={clear}
            className="rounded border border-zinc-700 px-3 py-1 text-sm text-red-400 hover:bg-zinc-800"
            data-testid="logs-clear"
          >
            Clear
          </button>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <select
          value={level}
          onChange={(e) => {
            setLevel(e.target.value);
            setOffset(0);
          }}
          className="rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-sm"
          data-testid="logs-level"
        >
          {LEVELS.map((l) => (
            <option key={l} value={l}>
              {l === "" ? "All levels" : l}
            </option>
          ))}
        </select>
        <input
          value={kind}
          onChange={(e) => {
            setKind(e.target.value);
            setOffset(0);
          }}
          placeholder="Kind (http, server, …)"
          className="rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-sm"
          data-testid="logs-kind"
        />
        <input
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setOffset(0);
          }}
          placeholder="Search…"
          className="rounded border border-zinc-700 bg-zinc-900 px-2 py-1 text-sm"
          data-testid="logs-search"
        />
        <button
          type="button"
          onClick={() => setSort((s) => (s === "desc" ? "asc" : "desc"))}
          className="rounded border border-zinc-700 px-2 py-1 text-sm hover:bg-zinc-800"
          data-testid="logs-sort"
        >
          {sort === "desc" ? "Newest first" : "Oldest first"}
        </button>
        <button
          type="button"
          onClick={() => query()}
          className="rounded border border-zinc-700 px-2 py-1 text-sm hover:bg-zinc-800"
          data-testid="logs-refresh"
        >
          Refresh
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      <p className="mt-2 text-xs text-zinc-500" data-testid="logs-count">
        {total} entries
      </p>
      {entries.length === 0 ? (
        <p className="mt-6 text-sm text-zinc-500" data-testid="logs-empty">
          No log entries match.
        </p>
      ) : (
        <table className="mt-2 w-full font-mono text-xs" data-testid="logs-table">
          <thead>
            <tr className="text-left text-zinc-400">
              <th className="py-1">Timestamp</th>
              <th>Level</th>
              <th>Kind</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e) => (
              <tr key={e.id} className="border-t border-zinc-800">
                <td className="py-1 text-zinc-500">{e.timestamp}</td>
                <td
                  className={
                    e.level === "ERROR" || e.level === "CRITICAL"
                      ? "text-red-400"
                      : e.level === "WARNING"
                        ? "text-amber-400"
                        : "text-green-400"
                  }
                >
                  {e.level}
                </td>
                <td className="text-zinc-400">{e.kind}</td>
                <td>{e.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <div className="mt-3 flex items-center gap-2 text-sm">
        <button
          type="button"
          disabled={offset === 0}
          onClick={() => setOffset((o) => Math.max(0, o - PAGE_SIZE))}
          className="rounded border border-zinc-700 px-2 py-1 disabled:opacity-40"
          data-testid="logs-prev"
        >
          Prev
        </button>
        <span className="text-zinc-500" data-testid="logs-page">
          Page {page} / {pages}
        </span>
        <button
          type="button"
          disabled={offset + PAGE_SIZE >= total}
          onClick={() => setOffset((o) => o + PAGE_SIZE)}
          className="rounded border border-zinc-700 px-2 py-1 disabled:opacity-40"
          data-testid="logs-next"
        >
          Next
        </button>
      </div>
    </div>
  );
}
