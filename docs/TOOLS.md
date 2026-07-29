# Tools

## sfx_search (portmanteau)

Single tool with 5 operations via `operation` parameter.

| Operation | Description |
|-----------|-------------|
| search | Query FreeSound CC0 database. Supports duration filter, tags, pagination. |
| download | Download sound by ID to local disk. Cached in SQLite. |
| tag | Assign user tag to a cached sound. |
| list_local | List cached sounds, optionally filtered by tag. |
| describe | Full metadata: name, description, duration, samplerate, tags, preview URL. |
| play | Play a local sound file via system default player or winsound (Windows .wav). |

## show_sfx_browser_card

No arguments. Prefab UI card showing all locally cached sounds.

## Return Format

```json
{"success": true, "message": "...", "data": {...}}
```
