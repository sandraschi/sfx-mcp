from __future__ import annotations

import logging
import os
from typing import Annotated, Literal

import httpx
from pydantic import Field

from ..config import config
from ..deps import get_cache, get_freesound
from ..server import mcp

logger = logging.getLogger("sfx-mcp")

_READ_ONLY = {"readonly": True}
_MUTATING = {}


def _error_response(error: str, error_type: str = "general", **kwargs) -> dict:
    logger.exception("Tool error: %s [%s]", error, error_type)
    return {
        "success": False,
        "error": error,
        "error_type": error_type,
        **kwargs,
    }


@mcp.tool(annotations=_READ_ONLY)
async def sfx_search(
    operation: Annotated[
        Literal["search", "download", "tag", "list_local", "describe"],
        Field(description="Operation to perform."),
    ],
    query: Annotated[
        str | None,
        Field(description="Search query text. Required for: search."),
    ] = None,
    duration_max: Annotated[
        int,
        Field(
            description="Maximum sound duration in seconds. Only for: search.",
            ge=1,
        ),
    ] = 30,
    tags: Annotated[
        list[str] | None,
        Field(description="Filter by FreeSound tags. Only for: search."),
    ] = None,
    page: Annotated[
        int,
        Field(description="Page number for paginated results. Only for: search.", ge=1),
    ] = 1,
    sound_id: Annotated[
        int | None,
        Field(description="FreeSound sound ID. Required for: download, tag, describe."),
    ] = None,
    destination: Annotated[
        str | None,
        Field(description="Download directory. Defaults to SFX_LOCAL_PATH. Only for: download."),
    ] = None,
    tag_name: Annotated[
        str | None,
        Field(description="Tag to assign to a sound. Required for: tag."),
    ] = None,
    tag_filter: Annotated[
        str | None,
        Field(description="Filter local cache by tag. Only for: list_local."),
    ] = None,
) -> dict:
    """[RATIONALE] Consolidated portmanteau for all FreeSound operations —
    search, download, tag, list local cache, and describe metadata — to avoid
    tool explosion while keeping related sound-effect operations grouped.

    Operations:
    - search: Query FreeSound's CC0 sound database. Supports duration filter, tags, pagination.
    - download: Download a sound's original file to local disk. Requires sound_id.
    - tag: Assign a user-defined tag to a locally cached sound.
    - list_local: List all locally cached sounds, optionally filtered by tag.
    - describe: Get full metadata for a specific sound from FreeSound.

    ## Return Format
    {"success": bool, "message": str, "data": {...}}

    ## Examples
    sfx_search(operation="search", query="thunder", duration_max=30)
    sfx_search(operation="download", sound_id=12345)
    sfx_search(operation="list_local", tag_filter="sfx")
    """
    if not config.has_api_key:
        return _error_response(
            "FreeSound API key not configured. Set FREESOUND_API_KEY in .env",
            "auth",
            suggestions=[
                "Create a .env file with FREESOUND_API_KEY=your_key",
                "Get a key at https://freesound.org/apiv2/apply",
            ],
        )

    api = get_freesound()
    cache = get_cache()

    try:
        if operation == "search":
            return await _handle_search(api, query, duration_max, tags, page)
        elif operation == "download":
            return await _handle_download(api, cache, sound_id, destination)
        elif operation == "tag":
            return _handle_tag(cache, sound_id, tag_name)
        elif operation == "list_local":
            return _handle_list_local(cache, tag_filter)
        elif operation == "describe":
            return await _handle_describe(api, sound_id)
        else:
            return _error_response(f"Unknown operation: {operation}", "validation")
    except RuntimeError as e:
        return _error_response(str(e), "api_error")
    except Exception as e:
        return _error_response(str(e), "unexpected")


async def _handle_search(
    api, query: str | None, duration_max: int, tags: list[str] | None, page: int
) -> dict:
    if not query:
        return _error_response("query is required for search", "validation")
    result = await api.search(query, duration_max=duration_max, tags=tags, page=page)
    sounds = result.get("results", [])
    count = result.get("count", 0)
    more = bool(result.get("next"))

    items = []
    for s in sounds:
        items.append(
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "duration": s.get("duration"),
                "samplerate": s.get("samplerate"),
                "tags": s.get("tags", []),
                "preview": (
                    s.get("previews", {}).get("preview-lq-mp3")
                    if s.get("previews")
                    else None
                ),
                "url": s.get("url"),
            }
        )

    return {
        "success": True,
        "message": f"Found {count} sounds. Showing page {page}.",
        "data": {
            "sounds": items,
            "total": count,
            "page": page,
            "has_more": more,
            "query": query,
        },
    }


async def _handle_download(
    api, cache, sound_id: int | None, destination: str | None
) -> dict:
    if sound_id is None:
        return _error_response("sound_id is required for download", "validation")

    dest_dir = destination or config.SFX_LOCAL_PATH
    os.makedirs(dest_dir, exist_ok=True)

    detail = await api.get_sound_detail(sound_id)
    name = detail.get("name", f"sound_{sound_id}")
    safe_name = "".join(c for c in name if c.isalnum() or c in " ._-").strip()
    if not safe_name:
        safe_name = f"sound_{sound_id}"

    ext = detail.get("type", "wav")
    file_path = os.path.join(dest_dir, f"{safe_name}.{ext}")

    download_url = await api.get_download_url(sound_id)
    if not download_url:
        return _error_response(
            "No download URL available for this sound", "api_error"
        )

    async with httpx.AsyncClient(timeout=120.0) as dl_client:
        response = await dl_client.get(
            download_url,
            headers={"Authorization": f"Token {config.FREESOUND_API_KEY}"},
            follow_redirects=True,
        )
        response.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(response.content)

    cache.add_sound(
        sound_id=sound_id,
        name=name,
        description=detail.get("description", ""),
        duration=detail.get("duration", 0),
        samplerate=detail.get("samplerate", 0),
        tags=detail.get("tags", []),
        local_path=file_path,
    )

    return {
        "success": True,
        "message": f"Downloaded '{name}' to {file_path}",
        "data": {
            "sound_id": sound_id,
            "name": name,
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
        },
    }


def _handle_tag(cache, sound_id: int | None, tag_name: str | None) -> dict:
    if sound_id is None or not tag_name:
        return _error_response(
            "sound_id and tag_name are required for tag", "validation"
        )
    if not cache.sound_exists(sound_id):
        return _error_response(
            f"Sound {sound_id} is not in the local cache. Download it first.",
            "not_found",
            suggestions=["Use operation='download' with this sound_id first"],
        )
    cache.add_tag(sound_id, tag_name)
    return {
        "success": True,
        "message": f"Tagged sound {sound_id} with '{tag_name}'",
        "data": {"sound_id": sound_id, "tag": tag_name},
    }


def _handle_list_local(cache, tag_filter: str | None) -> dict:
    sounds = cache.list_local(tag_filter=tag_filter)
    return {
        "success": True,
        "message": f"Found {len(sounds)} local sound(s)",
        "data": {"sounds": sounds, "count": len(sounds), "tag_filter": tag_filter},
    }


async def _handle_describe(api, sound_id: int | None) -> dict:
    if sound_id is None:
        return _error_response("sound_id is required for describe", "validation")
    detail = await api.get_sound_detail(sound_id)
    return {
        "success": True,
        "message": f"Metadata for sound {sound_id}",
        "data": {
            "id": detail.get("id"),
            "name": detail.get("name"),
            "description": detail.get("description", ""),
            "duration": detail.get("duration"),
            "samplerate": detail.get("samplerate"),
            "filesize": detail.get("filesize"),
            "bitrate": detail.get("bitrate"),
            "type": detail.get("type"),
            "tags": detail.get("tags", []),
            "preview": (
                detail.get("previews", {}).get("preview-lq-mp3")
                if detail.get("previews")
                else None
            ),
            "url": detail.get("url"),
            "download_url": detail.get("download"),
        },
    }
