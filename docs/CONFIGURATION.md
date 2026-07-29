# Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| FREESOUND_API_KEY | — | Required. FreeSound API v2 key. |
| SFX_LOCAL_PATH | data/sounds | Download directory |
| SFX_DB_PATH | data/sfx_cache.db | SQLite cache path |
| MCP_PORT | — | HTTP mode port (set to 11120 for HTTP) |
| MCP_HOST | 127.0.0.1 | HTTP bind address |

Copy `.env.example` to `.env` and set FREESOUND_API_KEY.
