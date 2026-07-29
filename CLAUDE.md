# sfx-mcp — Agent Instructions

## Entry points
- `src/sfx_mcp/server.py` — FastMCP + FastAPI setup
- `src/sfx_mcp/tools/sfx_search.py` — `sfx_search` portmanteau (5 ops)
- `src/sfx_mcp/services/freesound.py` — FreeSound API client
- `src/sfx_mcp/services/cache.py` — SQLite cache layer

## Standards
- Python: ruff, uv, FastMCP >=3.4.4
- Port: 11120 (backend API + MCP /mcp)
- Required: FREESOUND_API_KEY in .env

## Commands
```powershell
uv sync
uv run python -m sfx_mcp
uv run python run_server.py
uv run pytest
ruff check src/
ruff format src/
```
