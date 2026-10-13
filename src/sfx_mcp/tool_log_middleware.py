"""FastMCP middleware: log every tool call into the standard ring buffer.

Implements the WEBAPP_LOGS_PAGE.md requirement that tool calls log with
``kind: tool_call`` (level ERROR on failure) — from one central seam instead
of per-tool edits. Wired via ``mcp.add_middleware`` in server.py.
"""

from __future__ import annotations

import time
from typing import Any

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools.base import ToolResult

from sfx_mcp.activity_log import log_activity


class ToolActivityMiddleware(Middleware):
    """Record tool calls as kind=tool_call (ERROR on failure)."""

    async def on_call_tool(
        self,
        context: MiddlewareContext[Any],
        call_next: CallNext[Any, ToolResult],
    ) -> ToolResult:
        params = context.message
        name = str(getattr(params, "name", "unknown"))
        args = getattr(params, "arguments", None) or {}
        arg_keys = sorted(args.keys()) if isinstance(args, dict) else []
        start = time.monotonic()
        try:
            result = await call_next(context)
        except Exception as e:
            ms = int((time.monotonic() - start) * 1000)
            log_activity(
                kind="tool_call",
                detail=f"{name} (error: {type(e).__name__})",
                level="ERROR",
                meta={"tool": name, "arg_keys": arg_keys, "duration_ms": ms},
            )
            raise
        ms = int((time.monotonic() - start) * 1000)
        structured = getattr(result, "structured_content", None)
        returned_false = isinstance(structured, dict) and structured.get("success") is False
        failed = bool(getattr(result, "is_error", False)) or returned_false
        log_activity(
            kind="tool_call",
            detail=f"{name} ({'fail' if failed else 'ok'})",
            level="ERROR" if failed else "INFO",
            meta={"tool": name, "arg_keys": arg_keys, "duration_ms": ms},
        )
        return result
