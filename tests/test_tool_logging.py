"""Tests for tool_call ring-buffer logging via FastMCP middleware."""

from __future__ import annotations

import os

import pytest
from fastmcp.exceptions import NotFoundError

os.environ.setdefault("FREESOUND_API_KEY", "")

from sfx_mcp.activity_log import clear_logs, query_logs  # noqa: E402
from sfx_mcp.server import mcp  # noqa: E402
from sfx_mcp.tools import register_all_tools  # noqa: E402

register_all_tools(mcp)


@pytest.mark.asyncio
async def test_tool_call_logged_fail_without_key() -> None:
    # No API key in CI: list_local returns {"success": False} without raising.
    # The middleware must still record it as an ERROR tool_call entry.
    clear_logs()
    result = await mcp.call_tool("sfx_search", {"operation": "list_local"})
    assert result is not None
    logged = query_logs(kind="tool_call")
    assert logged["total"] >= 1
    entry = logged["entries"][0]
    assert entry["level"] == "ERROR"
    assert entry["meta"]["tool"] == "sfx_search"
    assert "(fail)" in entry["detail"]


@pytest.mark.asyncio
async def test_tool_call_logged_error() -> None:
    clear_logs()
    with pytest.raises(NotFoundError):
        await mcp.call_tool("no_such_tool_xyz", {})
    logged = query_logs(kind="tool_call")
    assert logged["total"] >= 1
    assert logged["entries"][0]["level"] == "ERROR"
