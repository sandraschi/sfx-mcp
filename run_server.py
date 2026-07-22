"""PyInstaller entry point / dual-transport runner.

Detects MCP_PORT env var to decide transport mode:
- MCP_PORT set → HTTP mode (uvicorn on FastAPI + mounted MCP SSE)
- MCP_PORT unset → stdio mode (FastMCP stdio)
"""
import os
import sys

sys.path.insert(0, "src")

from sfx_mcp.server import app, mcp
from sfx_mcp.config import config


def main():
    port = os.environ.get("MCP_PORT") or os.environ.get("PORT")
    if port:
        host = os.environ.get("MCP_HOST", "127.0.0.1")
        import uvicorn

        uvicorn.run(app, host=host, port=int(port), log_level="info")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
