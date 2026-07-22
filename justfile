lint:
    uv run ruff check src/

serve:
    uv run python -m sfx_mcp

test:
    uv run pytest

fmt:
    uv run ruff format src/

serve-http:
    uv run python run_server.py
