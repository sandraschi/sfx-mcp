"""Tests for sfx-mcp services and config."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sfx_mcp.config import Config


def test_config_defaults():
    c = Config()
    assert c.API_BASE_URL == "https://freesound.org/apiv2"
    assert c.BACKEND_PORT == 11120
    assert c.FRONTEND_PORT == 11121
    assert not c.has_api_key


def test_has_api_key():
    c = Config(FREESOUND_API_KEY="test_key_123")
    assert c.has_api_key


def test_config_defaults_paths():
    c = Config()
    assert c.SFX_LOCAL_PATH == "data/sounds"
    assert c.SFX_DB_PATH == "data/sfx_cache.db"
