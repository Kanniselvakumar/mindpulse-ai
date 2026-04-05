from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def isolated_env(monkeypatch, tmp_path):
    from shared.config import get_settings

    db_path = tmp_path / "test_wellness.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("STREAMLIT_FORCE_LOCAL_BACKEND", "true")
    get_settings.cache_clear()

    import backend.app_platform as platform

    platform._BOOTSTRAPPED = False
    platform.bootstrap()
    return db_path
