# SFX-MCP Agent Instructions

## Quick Reference

| Item | Value |
|------|-------|
| Repo | `D:\Dev\repos\sfx-mcp` |
| Backend port | 11120 (HTTP/MCP) |
| Frontend port | 11121 (reserved) |
| MCP endpoint | `http://127.0.0.1:11120/mcp` (both `/mcp` and `/mcp/` accepted) |
| Health endpoint | `http://127.0.0.1:11120/api/health` |
| Entry point | `sfx_mcp.__main__:main` |
| Package manager | `uv` |

## Commands

```powershell
# Install
uv sync

# Run (stdio — for Claude Desktop, Cursor)
uv run python -m sfx_mcp

# Run (HTTP — for webapp)
uv run python run_server.py

# Lint
uv run ruff check src/

# Format
uv run ruff format src/
```

## Deployment

- `FREESOUND_API_KEY` env var is required for all API operations
- SQLite cache is at `data/sfx_cache.db`
- Downloaded sounds go to `data/sounds/` by default
