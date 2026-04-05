from __future__ import annotations

from typing import Any

import requests

from backend import app_platform as local_platform
from shared.config import get_settings


def _use_remote_api() -> bool:
    settings = get_settings()
    return bool(settings.api_base_url) and not settings.force_local_backend


def _call_api(method: str, path: str, **kwargs) -> Any:
    settings = get_settings()
    response = requests.request(
        method,
        f"{settings.api_base_url}{path}",
        timeout=15,
        **kwargs,
    )
    response.raise_for_status()
    return response.json()


def bootstrap() -> None:
    local_platform.bootstrap()


def register_user(payload: dict[str, Any]) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", "/api/auth/register", json=payload)
        except Exception:
            pass
    return local_platform.register_user(payload)


def login_user(payload: dict[str, Any]) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", "/api/auth/login", json=payload)
        except Exception:
            pass
    return local_platform.login_user(payload)


def get_account(user_id: str) -> dict[str, Any] | None:
    if _use_remote_api():
        try:
            return _call_api("GET", f"/api/auth/account/{user_id}")
        except Exception:
            pass
    return local_platform.get_account(user_id)


def get_profile(user_id: str) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("GET", f"/api/profile/{user_id}")
        except Exception:
            pass
    return local_platform.get_profile(user_id)


def update_profile(payload: dict[str, Any]) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", "/api/profile", json=payload)
        except Exception:
            pass
    return local_platform.update_profile(payload)


def submit_check_in(payload: dict[str, Any]) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", "/api/checkins", json=payload)
        except Exception:
            pass
    return local_platform.submit_check_in(payload)


def get_dashboard(user_id: str, days: int = 30) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("GET", f"/api/dashboard/{user_id}", params={"days": days})
        except Exception:
            pass
    return local_platform.get_dashboard(user_id, days)


def get_notifications(user_id: str) -> list[dict[str, Any]]:
    if _use_remote_api():
        try:
            return _call_api("GET", f"/api/notifications/{user_id}")
        except Exception:
            pass
    return local_platform.get_notifications(user_id)


def get_alert_provider_status() -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("GET", "/api/alerts/provider-status")
        except Exception:
            pass
    return local_platform.get_alert_provider_status()


def get_ml_overview() -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("GET", "/api/ml/overview")
        except Exception:
            pass
    return local_platform.get_ml_overview()


def support_chat(payload: dict[str, Any]) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", "/api/assistant", json=payload)
        except Exception:
            pass
    return local_platform.support_chat(payload)


def get_resources(campus: str, risk_level: str = "Normal") -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api(
                "GET",
                "/api/resources",
                params={"campus": campus, "risk_level": risk_level},
            )
        except Exception:
            pass
    return local_platform.get_resources(campus, risk_level)


def list_peer_posts() -> list[dict[str, Any]]:
    if _use_remote_api():
        try:
            return _call_api("GET", "/api/peer-posts")
        except Exception:
            pass
    return local_platform.list_peer_posts()


def create_peer_post(payload: dict[str, Any]) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", "/api/peer-posts", json=payload)
        except Exception:
            pass
    return local_platform.create_peer_post(payload)


def get_buddy_matches(user_id: str) -> list[dict[str, Any]]:
    if _use_remote_api():
        try:
            return _call_api("GET", f"/api/buddy-matches/{user_id}")
        except Exception:
            pass
    return local_platform.get_buddy_matches(user_id)


def get_admin_overview(days: int = 30) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("GET", "/api/admin/overview", params={"days": days})
        except Exception:
            pass
    return local_platform.get_admin_overview(days)
