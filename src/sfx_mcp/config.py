from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Relative paths resolve against the repo root, never the CWD: Claude Desktop
# spawns stdio servers with cwd=C:\Windows\System32 (BUG-063).
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _repo_path(value: str) -> str:
    return value if Path(value).is_absolute() else str(_REPO_ROOT / value)


@dataclass
class Config:
    FREESOUND_API_KEY: str = field(default_factory=lambda: os.getenv("FREESOUND_API_KEY", ""))
    SFX_LOCAL_PATH: str = field(
        default_factory=lambda: _repo_path(os.getenv("SFX_LOCAL_PATH", "data/sounds"))
    )
    SFX_DB_PATH: str = field(
        default_factory=lambda: _repo_path(os.getenv("SFX_DB_PATH", "data/sfx_cache.db"))
    )
    API_BASE_URL: str = "https://freesound.org/apiv2"
    BACKEND_PORT: int = 11120
    FRONTEND_PORT: int = 11121

    @property
    def has_api_key(self) -> bool:
        return bool(self.FREESOUND_API_KEY)


config = Config()
