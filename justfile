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

# Bootstrap: install dev deps + pre-commit hook
bootstrap:
    uv sync --group dev
    uv run pre-commit install
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green

# Pack MCPB bundle
mcpb-pack:
    mcpb pack . dist/sfx-mcp-v$(uv run python -c "import sfx_mcp; print(sfx_mcp.__version__)").mcpb

# Run all gates
gates-green: lint fmt test
    Write-Host "All gates passed." -ForegroundColor Green
