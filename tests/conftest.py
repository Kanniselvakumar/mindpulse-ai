from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def isolated_env(monkeypatch):
    import tempfile
    from shared.config import get_settings

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_wellness.db"
        monkeypatch.setenv("DATABASE_PATH", str(db_path))
        monkeypatch.setenv("APP_SECRET_KEY", "test-secret-key")
        monkeypatch.setenv("STREAMLIT_FORCE_LOCAL_BACKEND", "true")
        get_settings.cache_clear()

        import backend.app_platform as platform
        from backend.services.risk_engine import risk_engine

        platform._BOOTSTRAPPED = False
        platform.bootstrap()
        risk_engine.reset_to_default_dataset()
        try:
            yield db_path
        finally:
            risk_engine.reset_to_default_dataset()


