# Development

## Setup

```powershell
cp .env.example .env
# Edit .env: set FREESOUND_API_KEY=your_key
uv sync
```

## Run

```powershell
# stdio mode
uv run python -m sfx_mcp

# HTTP mode
uv run python run_server.py
```

## Lint

```powershell
ruff check src/
ruff format src/
```

## Test

```powershell
uv run pytest
```
