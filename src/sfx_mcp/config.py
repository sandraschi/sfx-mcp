from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    FREESOUND_API_KEY: str = field(
        default_factory=lambda: os.getenv("FREESOUND_API_KEY", "")
    )
    SFX_LOCAL_PATH: str = field(
        default_factory=lambda: os.getenv("SFX_LOCAL_PATH", "data/sounds")
    )
    SFX_DB_PATH: str = field(
        default_factory=lambda: os.getenv("SFX_DB_PATH", "data/sfx_cache.db")
    )
    API_BASE_URL: str = "https://freesound.org/apiv2"
    BACKEND_PORT: int = 11120
    FRONTEND_PORT: int = 11121

    @property
    def has_api_key(self) -> bool:
        return bool(self.FREESOUND_API_KEY)


config = Config()
