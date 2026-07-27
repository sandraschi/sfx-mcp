"""REST API for FreeSound search (fleet consumers e.g. mixx-dj-mcp)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .config import config
from .tools.sfx_search import (
    _handle_describe,
    _handle_download,
    _handle_list_local,
    _handle_search,
)

router = APIRouter()


def _api():
    from .deps import get_cache, get_freesound

    return get_freesound(), get_cache()


def _normalize_sound(item: dict) -> dict:
    preview = item.get("preview") or item.get("preview_url") or ""
    return {
        "id": item.get("id"),
        "name": item.get("name") or "Untitled",
        "duration": float(item.get("duration") or 0),
        "tags": item.get("tags") or [],
        "preview_url": preview,
        "license": item.get("license") or "CC0",
        "url": item.get("url"),
    }


@router.get("/search")
async def search_sounds(
    q: str = Query(..., min_length=1, description="Search query"),
    duration_max: int = Query(30, ge=1, le=300),
    page: int = Query(1, ge=1),
    tag: str | None = Query(None, description="Optional tag filter"),
):
    """Search CC0 sounds on FreeSound."""
    if not config.has_api_key:
        raise HTTPException(
            status_code=503,
            detail="FreeSound API key not configured (FREESOUND_API_KEY)",
        )
    tags = [tag] if tag else None
    api, _cache = _api()
    payload = await _handle_search(api, q, duration_max, tags, page)
    if not payload.get("success"):
        raise HTTPException(status_code=400, detail=payload.get("error") or "Search failed")
    data = payload.get("data") or {}
    sounds = [_normalize_sound(s) for s in data.get("sounds") or []]
    return {
        "success": True,
        "results": sounds,
        "sounds": sounds,
        "total": data.get("total", len(sounds)),
        "page": data.get("page", page),
        "has_more": data.get("has_more", False),
        "query": q,
        "message": payload.get("message"),
    }


@router.get("/local")
async def list_local_sounds(tag: str | None = Query(None)):
    """List sounds cached locally by sfx-mcp."""
    _api_freesound, cache = _api()
    payload = _handle_list_local(cache, tag)
    sounds = payload.get("data", {}).get("sounds") or []
    return {
        "success": True,
        "results": sounds,
        "total": len(sounds),
        "message": payload.get("message"),
    }


class DownloadRequest(BaseModel):
    sound_id: int = Field(..., ge=1)
    destination: str | None = None


@router.post("/download")
async def download_sound(req: DownloadRequest):
    """Download a sound to the local sfx-mcp cache."""
    if not config.has_api_key:
        raise HTTPException(status_code=503, detail="FreeSound API key not configured")
    api, cache = _api()
    payload = await _handle_download(api, cache, req.sound_id, req.destination)
    if not payload.get("success"):
        raise HTTPException(status_code=400, detail=payload.get("error") or "Download failed")
    return payload


@router.get("/{sound_id}")
async def describe_sound(sound_id: int):
    """Metadata for one FreeSound item."""
    if not config.has_api_key:
        raise HTTPException(status_code=503, detail="FreeSound API key not configured")
    api, _cache = _api()
    payload = await _handle_describe(api, sound_id)
    if not payload.get("success"):
        raise HTTPException(status_code=404, detail=payload.get("error") or "Not found")
    data = payload.get("data") or {}
    return {"success": True, "data": _normalize_sound({**data, "preview": data.get("preview")})}
