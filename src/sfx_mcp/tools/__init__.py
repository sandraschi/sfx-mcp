import logging

logger = logging.getLogger("sfx-mcp")


def register_all_tools(mcp: "FastMCP") -> None:  # noqa: F821
    """Import tool modules to register them on the MCP server.

    FastMCP registers tools at import time via @mcp.tool decorator.
    Each module is imported for its side effect of registering tools.
    """
    import importlib

    _modules = [
        "sfx_mcp.tools.sfx_search",
        "sfx_mcp.tools.prefab_cards",
    ]
    for mod_name in _modules:
        try:
            importlib.import_module(mod_name)
            logger.debug("Registered tools from %s", mod_name)
        except Exception:
            logger.exception("Failed to import tool module %s", mod_name)
            raise
