from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from .config import config
from .deps import get_cache, get_freesound
from .tools import register_all_tools

logger = logging.getLogger("sfx-mcp")

mcp = FastMCP(
    "sfx-mcp",
    instructions="Search and download CC0-licensed sound effects from FreeSound.org",
    version="0.1.0",
)

app = FastAPI(title="SFX-MCP", version="0.1.0")

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


def main():
    os.makedirs(config.SFX_LOCAL_PATH, exist_ok=True)

    register_all_tools(mcp)

    port = os.environ.get("MCP_PORT") or os.environ.get("PORT")
    if port:
        import uvicorn

        host = os.environ.get("MCP_HOST", "127.0.0.1")

        mcp_sse = mcp.http_app()
        app.mount("/mcp", mcp_sse)

        logger.info("Starting SFX-MCP HTTP on %s:%s", host, port)
        uvicorn.run(app, host=host, port=int(port), log_level="info")
    else:
        logger.info("Starting SFX-MCP in stdio mode")
        mcp.run()


from .api_sounds import router as sounds_router  # noqa: E402

app.include_router(sounds_router, prefix="/api/sounds", tags=["sounds"])
