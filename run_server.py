"""PyInstaller entry point / dual-transport runner.

HTTP when MCP_PORT/PORT is set or `--serve` is passed, stdio otherwise
(`--stdio` forces it). The FastAPI app and its `/mcp` mount live in
`sfx_mcp.server`, so this file only chooses the transport - mounting the MCP
app here would create a second instance without the lifespan fix.
"""

import sys

sys.path.insert(0, "src")

from sfx_mcp.server import main  # noqa: E402

if __name__ == "__main__":
    main()
