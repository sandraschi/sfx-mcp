# SFX-MCP

FastMCP 3.4+ server wrapping the [FreeSound API](https://freesound.org/apiv2) for CC0-licensed sound effects search and download.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- FreeSound API key ([apply here](https://freesound.org/apiv2/apply))

## Setup

```bash
# Clone and enter directory
cd sfx-mcp

# Create .env with your API key
cp .env.example .env
# Edit .env: set FREESOUND_API_KEY=your_key

# Install dependencies
uv sync

# Run in stdio mode (for Claude Desktop, Cursor, etc.)
uv run python -m sfx_mcp

# Or run in HTTP mode (for webapp integration)
uv run python run_server.py
# Listens on http://127.0.0.1:11120
# MCP SSE endpoint: http://127.0.0.1:11120/mcp
# Health check: http://127.0.0.1:11120/api/health
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "sfx": {
      "command": "uv",
      "args": ["run", "--directory", "D:\\Dev\\repos\\sfx-mcp", "python", "-m", "sfx_mcp"]
    }
  }
}
```

## Tools

### `sfx_search` (portmanteau)

| Operation | Description |
|-----------|-------------|
| `search` | Query FreeSound for CC0 sounds. Filters: query, duration_max, tags, page. |
| `download` | Download a sound by ID to local disk. |
| `tag` | Assign a user tag to a cached sound (local SQLite). |
| `list_local` | List all locally cached sounds, optionally filtered by tag. |
| `describe` | Get full metadata for a sound (name, duration, samplerate, tags, preview URL). |

### `show_sfx_browser_card`

Prefab rich card showing all locally cached sounds with names, durations, and paths.

## Ports

| Service | Port |
|---------|------|
| Backend (HTTP/MCP) | 11120 |
| Frontend (reserved) | 11121 |

## License

MIT
