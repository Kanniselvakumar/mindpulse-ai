from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def main() -> None:
    try:
        from streamlit.web import cli as stcli
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Streamlit is not installed for this Python. Run: python -m pip install -r requirements.txt"
        ) from exc

    sys.argv = ["streamlit", "run", str(ROOT_DIR / "frontend" / "Home.py")]
    raise SystemExit(stcli.main())


if __name__ == "__main__":
    main()
