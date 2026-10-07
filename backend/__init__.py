from __future__ import annotations

from flask import Flask

from backend.api.routes import api_bp
from backend.app_platform import bootstrap


def create_app() -> Flask:
    bootstrap()
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.register_blueprint(api_bp)
    return app
