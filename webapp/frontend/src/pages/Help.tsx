export default function Help() {
  return (
    <div className="max-w-2xl">
      <h1 className="text-xl font-bold" data-testid="help-title">
        Help
      </h1>
      <section className="mt-4">
        <h2 className="font-semibold">What is this?</h2>
        <p className="mt-1 text-sm text-zinc-400">
          sfx-mcp wraps the FreeSound API for CC0 sound effects: one portmanteau MCP tool (`sfx_search`: search,
          download, tag, list_local, describe, play) plus this REST dashboard on port 11120. Sounds you download land in
          the local library; search and download need a FreeSound API key.
        </p>
      </section>
      <section className="mt-4">
        <h2 className="font-semibold">API / ports</h2>
        <ul className="mt-1 list-disc pl-5 text-sm text-zinc-400">
          <li>
            Backend <code className="font-mono">11120</code>: <code className="font-mono">/api/health</code>,{" "}
            <code className="font-mono">/api/sounds/search</code>, <code className="font-mono">/api/sounds/local</code>,{" "}
            <code className="font-mono">/api/sounds/download</code>, <code className="font-mono">/api/tools</code>,{" "}
            <code className="font-mono">/api/logs</code> (+ <code className="font-mono">/stats</code>,{" "}
            <code className="font-mono">/export</code>, <code className="font-mono">DELETE</code>),{" "}
            <code className="font-mono">/mcp</code>, <code className="font-mono">/docs</code>
          </li>
          <li>
            Frontend dev <code className="font-mono">11121</code> (<code className="font-mono">bun run dev</code> in{" "}
            <code className="font-mono">webapp/frontend/</code>, proxies <code className="font-mono">/api</code> to
            11120)
          </li>
        </ul>
      </section>
      <section className="mt-4">
        <h2 className="font-semibold">Fixing common errors</h2>
        <ul className="mt-1 list-disc pl-5 text-sm text-zinc-400">
          <li>
            <code className="font-mono">503 key not configured</code> — set{" "}
            <code className="font-mono">FREESOUND_API_KEY</code> in <code className="font-mono">.env</code> (apply at
            freesound.org/apiv2/apply). Library, Tools and Logs work without a key.
          </li>
          <li>
            <code className="font-mono">GET / 404</code> — frontend not built. Run{" "}
            <code className="font-mono">bun run build</code> in <code className="font-mono">webapp/frontend/</code> so{" "}
            <code className="font-mono">webapp/frontend/dist/</code> exists.
          </li>
        </ul>
      </section>
      <section className="mt-4">
        <h2 className="font-semibold">FAQ</h2>
        <p className="mt-1 text-sm text-zinc-400">
          MCP server (stdio): <code className="font-mono">uv run python -m sfx_mcp</code>. HTTP daemon:{" "}
          <code className="font-mono">uv run python run_server.py</code> with{" "}
          <code className="font-mono">MCP_PORT=11120</code> (or <code className="font-mono">.\start.ps1</code>). Tests:{" "}
          <code className="font-mono">uv run pytest tests\ -q</code>.
        </p>
      </section>
    </div>
  );
}
