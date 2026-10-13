from __future__ import annotations

import logging

from ..deps import get_cache
from ..server import mcp

logger = logging.getLogger("sfx-mcp")

_READ_ONLY = {"readonly": True}


@mcp.tool(app=True, annotations=_READ_ONLY)
async def show_sfx_browser_card() -> dict:
    """Show locally cached sound effects as a rich in-chat Prefab card.

    Displays sound names, duration, tags, and local file paths for every
    sound that has been downloaded. Useful for browsing your SFX library
    without leaving the chat.

    ## Return Format
    {"success": bool, "content": str, "structured_content": {...}}
    """
    try:
        from prefab_ui import PrefabApp
        from prefab_ui.components import Div, Heading, Row, Text
    except ImportError:
        cache = get_cache()
        sounds = cache.list_local()
        lines = [f"- {s['name']} ({s['duration']}s) [id={s['id']}]" for s in sounds]
        body = "\n".join(lines) if lines else "No sounds in local cache."
        return {
            "success": True,
            "content": f"## SFX Browser\n\n{body}",
        }

    cache = get_cache()
    sounds = cache.list_local()

    app = PrefabApp(title="SFX Browser")

    with Div():
        Heading(f"Local SFX Library ({len(sounds)} sounds)")

        if not sounds:
            Text("No sounds downloaded yet. Search FreeSound first.")
        else:
            for s in sounds:
                user_tags = s.get("user_tags", [])
                tag_str = f" Tags: {', '.join(user_tags)}" if user_tags else ""
                Row(
                    label=s.get("name", f"Sound #{s['id']}"),
                    value=f"{s.get('duration', 0)}s | {s.get('local_path', '')}{tag_str}",
                )

    return {
        "success": True,
        "content": f"Showing {len(sounds)} local sound(s)",
        "structured_content": app,
    }
