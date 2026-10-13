import { useEffect, useState } from "react";
import { type McpTool, api } from "../lib/api";

export default function Tools() {
  const [tools, setTools] = useState<McpTool[]>([]);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");

  useEffect(() => {
    api
      .tools()
      .then((d) => setTools(d.tools))
      .catch((e: Error) => setError(e.message));
  }, []);

  const filtered = tools.filter(
    (t) =>
      t.name.toLowerCase().includes(query.toLowerCase()) || t.description.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div>
      <h1 className="text-xl font-bold" data-testid="tools-title">
        Tools
      </h1>
      <p className="mt-1 text-sm text-zinc-400">Live inventory from the MCP server — no hardcoded lists.</p>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Filter tools…"
        className="mt-4 w-full max-w-sm rounded border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm"
        data-testid="tools-filter"
      />
      <ul className="mt-4 space-y-2" data-testid="tools-list">
        {filtered.map((t) => (
          <li key={t.name} className="rounded border border-zinc-800 bg-zinc-900 px-4 py-2">
            <div className="font-mono text-sm text-amber-400">{t.name}</div>
            <div className="text-sm text-zinc-400">{t.description || "—"}</div>
          </li>
        ))}
      </ul>
      {filtered.length === 0 && <p className="mt-4 text-sm text-zinc-500">No tools match.</p>}
    </div>
  );
}
