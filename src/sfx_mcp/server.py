from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .activity_log import (
    clear_logs,
    export_logs,
    install_log_handler,
    log_activity,
    log_stats,
    query_logs,
)
from .config import config
from .tool_log_middleware import ToolActivityMiddleware
from .tools import register_all_tools

logger = logging.getLogger("sfx-mcp")

mcp = FastMCP(
    "sfx-mcp",
    instructions="Search and download CC0-licensed sound effects from FreeSound.org",
    version="0.1.0",
)
mcp.add_middleware(ToolActivityMiddleware())

# Dual transport (fleet standard): stdio by default, streamable HTTP at /mcp.
# mcp_app must be created before the FastAPI app so its lifespan can be passed
# in at construction. Without that lifespan, HTTP requests reach the session
# manager before it starts and every call fails with a 500. The path="/" plus
# mount("/mcp") keeps the endpoint at exactly /mcp, matching SFX_MCP_URL.
mcp_app = mcp.http_app(path="/")

app = FastAPI(title="SFX-MCP", version="0.1.0", lifespan=mcp_app.lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:11116",
        "http://127.0.0.1:11116",
        "http://localhost:11117",
        "http://127.0.0.1:11117",
        "http://localhost:11121",
        "http://127.0.0.1:11121",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ],
    allow_origin_regex=r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$|^tauri://localhost$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "server": "sfx-mcp",
        "version": "0.1.0",
        "has_api_key": config.has_api_key,
    }


@app.get("/", include_in_schema=False)
async def root():
    return HTMLResponse(
        "<h1>sfx-mcp</h1>"
        "<p>FreeSound CC0 sound effects: search, download, local library.</p>"
        "<ul>"
        '<li><a href="/api/health">/api/health</a></li>'
        '<li><a href="/api/sounds/local">/api/sounds/local</a></li>'
        '<li><a href="/api/logs">/api/logs</a></li>'
        '<li><a href="/docs">/docs</a></li>'
        "</ul>"
    )


@app.get("/api/tools")
async def list_tools():
    try:
        tools = await mcp.list_tools()
        items = [
            {
                "name": t.name,
                "description": (t.description or "").splitlines()[0] if t.description else "",
            }
            for t in tools
        ]
    except Exception as e:
        return {"tools": [], "count": 0, "error": str(e)}
    return {"tools": items, "count": len(items)}


@app.get("/api/logs")
async def logs_query(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    level: str | None = Query(None),
    kind: str | None = Query(None),
    search: str | None = Query(None),
    sort: str = Query("desc"),
    after_id: str | None = Query(None),
):
    order = "asc" if sort == "asc" else "desc"
    return query_logs(
        limit=limit,
        offset=offset,
        level=level,
        kind=kind,
        search=search,
        sort=order,  # type: ignore[arg-type]
        after_id=after_id,
    )


@app.get("/api/logs/stats")
async def logs_stats():
    return log_stats()


@app.get("/api/logs/export")
async def logs_export(
    format: str = Query("json"),
    level: str | None = Query(None),
    kind: str | None = Query(None),
    search: str | None = Query(None),
    sort: str = Query("desc"),
):
    if format not in ("json", "csv"):
        format = "json"
    order = "asc" if sort == "asc" else "desc"
    body, media_type, filename = export_logs(
        format=format,
        level=level,
        kind=kind,
        search=search,
        sort=order,  # type: ignore[arg-type]
    )
    return Response(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.delete("/api/logs")
async def logs_clear():
    clear_logs()
    return {"success": True, "message": "Log buffer cleared."}


class _LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        start = time.monotonic()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            ms = int((time.monotonic() - start) * 1000)
            level = "ERROR" if status >= 500 else ("WARNING" if status >= 400 else "INFO")
            log_activity(
                kind="http",
                detail=f"{request.method} {request.url.path} -> {status} ({ms}ms)",
                level=level,
                meta={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "ms": ms,
                },
            )


app.add_middleware(_LogMiddleware)


class _McpPathAlias:
    """Accept /mcp as well as /mcp/ for the mounted MCP app.

    Starlette's Mount matches /mcp/ but hands the child an empty path for
    /mcp, so a POST to the documented URL came back 405 while /mcp/ worked.
    Rewriting before routing fixes both spellings; a 307 would not help
    because MCP clients do not follow redirects on POST.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http" and scope.get("path") == "/mcp":
            scope = dict(scope)
            scope["path"] = "/mcp/"
            scope["raw_path"] = b"/mcp/"
        await self.app(scope, receive, send)


app.add_middleware(_McpPathAlias)


def main():
    install_log_handler()
    os.makedirs(config.SFX_LOCAL_PATH, exist_ok=True)

    register_all_tools(mcp)

    argv = sys.argv[1:]
    port = os.environ.get("MCP_PORT") or os.environ.get("PORT")
    if "--port" in argv:
        index = argv.index("--port")
        if index + 1 < len(argv):
            port = argv[index + 1]
    if "--stdio" in argv:
        port = None
    elif "--serve" in argv and not port:
        port = "11120"

    if port:
        import uvicorn

        host = os.environ.get("MCP_HOST", "127.0.0.1")
        logger.info("Starting SFX-MCP HTTP on %s:%s (MCP endpoint /mcp)", host, port)
        uvicorn.run(app, host=host, port=int(port), log_level="info")
    else:
        logger.info("Starting SFX-MCP in stdio mode")
        mcp.run()


from .api_sounds import router as sounds_router  # noqa: E402

app.include_router(sounds_router, prefix="/api/sounds", tags=["sounds"])

# Mount last: the MCP app owns /mcp, the REST routes above keep their paths.
app.mount("/mcp", mcp_app)

_DIST = Path(__file__).resolve().parents[2] / "webapp" / "frontend" / "dist"
if (_DIST / "index.html").is_file():
    app.mount("/assets", StaticFiles(directory=str(_DIST / "assets")), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa_fallback(path: str):
        return HTMLResponse((_DIST / "index.html").read_text(encoding="utf-8"))
