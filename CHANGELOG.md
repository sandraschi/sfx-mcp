# Changelog

## 0.1.0 (2026-07-30)

- Initial release
- `sfx_search` portmanteau tool (5 ops: search, download, tag, list_local, describe)
- `show_sfx_browser_card` Prefab UI card
- Dual transport: stdio and HTTP
- REST API at /api/sounds/search, /api/sounds/local, /api/sounds/download, /api/sounds/{id}
- SQLite local cache for downloaded sounds
- CORS with Tailscale + Tauri support
