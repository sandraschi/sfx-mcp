export interface Sound {
  id: number;
  name: string;
  duration: number;
  tags: string[];
  preview_url: string;
  license: string;
  url?: string;
  local_path?: string;
}

export interface McpTool {
  name: string;
  description: string;
}

async function get<T>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return (await r.json()) as T;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(`${path}: ${r.status} ${text}`);
  }
  return (await r.json()) as T;
}

export const api = {
  health: () => get<{ status: string; server: string; version: string; has_api_key: boolean }>("/api/health"),
  search: (q: string) =>
    get<{ success: boolean; results: Sound[]; total: number; page: number; has_more: boolean }>(
      `/api/sounds/search?q=${encodeURIComponent(q)}`,
    ),
  local: (tag?: string) =>
    get<{ success: boolean; results: Sound[]; total: number }>(
      tag ? `/api/sounds/local?tag=${encodeURIComponent(tag)}` : "/api/sounds/local",
    ),
  download: (sound_id: number) => post<unknown>("/api/sounds/download", { sound_id }),
  tools: () => get<{ tools: McpTool[]; count: number }>("/api/tools"),
  status: () =>
    get<{
      status: string;
      version: string;
    }>("/api/health"),
};
