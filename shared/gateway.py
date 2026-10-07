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


def get_upcoming_events(days_ahead: int = 14) -> list[dict[str, Any]]:
    if _use_remote_api():
        try:
            return _call_api("GET", "/api/academic-calendar", params={"days_ahead": days_ahead})
        except Exception:
            pass
    return local_platform.get_upcoming_events(days_ahead)


def get_coping_plan(user_id: str) -> list[dict[str, Any]]:
    if _use_remote_api():
        try:
            return _call_api("GET", f"/api/coping-plan/{user_id}")
        except Exception:
            pass
    return local_platform.get_coping_plan(user_id)


def update_coping_plan_item(plan_id: int, completed: bool, feedback: str = "") -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", f"/api/coping-plan/{plan_id}", json={"completed": completed, "feedback": feedback})
        except Exception:
            pass
    return local_platform.update_coping_plan_item(plan_id, completed, feedback)


def request_appointment(student_id: str, slot_time: str, reason: str = "") -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", "/api/appointments", json={"student_id": student_id, "slot_time": slot_time, "reason": reason})
        except Exception:
            pass
    return local_platform.request_appointment(student_id, slot_time, reason)


def get_appointments(user_id: str, role: str = "student") -> list[dict[str, Any]]:
    if _use_remote_api():
        try:
            return _call_api("GET", f"/api/appointments/{user_id}", params={"role": role})
        except Exception:
            pass
    return local_platform.get_appointments(user_id, role)


def update_appointment_status(appt_id: int, status: str, notes: str = "") -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", f"/api/appointments/{appt_id}/status", json={"status": status, "notes": notes})
        except Exception:
            pass
    return local_platform.update_appointment_status(appt_id, status, notes)


def get_peer_circles() -> list[dict[str, Any]]:
    if _use_remote_api():
        try:
            return _call_api("GET", "/api/peer-circles")
        except Exception:
            pass
    return local_platform.get_peer_circles()


def join_peer_circle(circle_id: int, user_id: str) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", f"/api/peer-circles/{circle_id}/join", json={"user_id": user_id})
        except Exception:
            pass
    return local_platform.join_peer_circle(circle_id, user_id)


def get_cohort_overview(days: int = 30) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("GET", "/api/admin/cohorts", params={"days": days})
        except Exception:
            pass
    return local_platform.get_cohort_overview(days)


def upload_dataset(file_content: str | bytes, filename: str) -> dict[str, Any]:
    if _use_remote_api():
        try:
            str_content = file_content.decode("utf-8", errors="replace") if isinstance(file_content, bytes) else file_content
            return _call_api("POST", "/api/dataset/upload", json={"content": str_content, "filename": filename})
        except Exception:
            pass
    return local_platform.upload_and_evaluate_dataset(file_content, filename)


def retrain_model(file_content: str | bytes, filename: str) -> dict[str, Any]:
    if _use_remote_api():
        try:
            str_content = file_content.decode("utf-8", errors="replace") if isinstance(file_content, bytes) else file_content
            return _call_api("POST", "/api/dataset/retrain", json={"content": str_content, "filename": filename})
        except Exception:
            pass
    return local_platform.retrain_model_with_custom_dataset(file_content, filename)


def predict_realtime_sample(sample_dict: dict[str, Any]) -> dict[str, Any]:
    if _use_remote_api():
        try:
            return _call_api("POST", "/api/realtime/predict", json=sample_dict)
        except Exception:
            pass
    return local_platform.predict_realtime_sample(sample_dict)


def get_sample_wellness_csv() -> str:
    if _use_remote_api():
        try:
            res = _call_api("GET", "/api/dataset/sample")
            return res.get("csv", "")
        except Exception:
            pass
    return local_platform.get_sample_wellness_csv()


