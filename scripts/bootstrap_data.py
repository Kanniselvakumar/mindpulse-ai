from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from backend.app_platform import bootstrap
from shared.config import get_settings


if __name__ == "__main__":
    bootstrap()
    print(f"Database ready at: {get_settings().database_path}")
