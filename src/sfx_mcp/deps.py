"""Shared runtime singletons (avoids circular imports between server, tools, API)."""

from __future__ import annotations

import os

from .config import config
from .services.cache import SoundCache
from .services.freesound import FreeSoundAPI

_freesound_api: FreeSoundAPI | None = None
_sound_cache: SoundCache | None = None


def get_freesound() -> FreeSoundAPI:
    global _freesound_api
    if _freesound_api is None:
        _freesound_api = FreeSoundAPI(config.FREESOUND_API_KEY)
    return _freesound_api


def get_cache() -> SoundCache:
    global _sound_cache
    if _sound_cache is None:
        os.makedirs(os.path.dirname(config.SFX_DB_PATH) or ".", exist_ok=True)
        _sound_cache = SoundCache(config.SFX_DB_PATH)
    return _sound_cache
