# sfx-mcp Skill

## What it does

FastMCP 3.4+ server wrapping the FreeSound API for CC0-licensed sound effects search and download.

## Tools

### sfx_search (portmanteau)

| Operation | Description | Required Params |
|-----------|-------------|----------------|
| search | Query FreeSound for CC0 sounds | query, duration_max, tags, page |
| download | Download sound by ID to local disk | sound_id |
| tag | Assign a user tag to a cached sound | sound_id, tag_name |
| list_local | List locally cached sounds | tag_filter (optional) |
| describe | Get full metadata for a sound | sound_id |

### show_sfx_browser_card

Prefab UI card listing all locally cached sounds with names, durations, and paths.

## Return Format

```json
{"success": true, "message": "...", "data": {...}}
```

## Configuration

- `FREESOUND_API_KEY` — Required. FreeSound API v2 key.
- `SFX_LOCAL_PATH` — Download directory (default: data/sounds)
- `SFX_DB_PATH` — SQLite cache path (default: data/sfx_cache.db)
- `MCP_PORT` — HTTP mode port (default: 11120)
