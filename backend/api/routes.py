from __future__ import annotations

from collections.abc import Callable

from flask import Blueprint, jsonify, request

from backend.app_platform import (
    create_peer_post,
    get_account,
    get_admin_overview,
    get_alert_provider_status,
    get_ml_overview,
    get_buddy_matches,
    get_dashboard,
    get_notifications,
    get_profile,
    get_resources,
    list_peer_posts,
    login_user,
    register_user,
    submit_check_in,
    support_chat,
    update_profile,
)
from shared.config import get_settings


api_bp = Blueprint("api", __name__, url_prefix="/api")


def _respond(action: Callable[[], object], success_status: int = 200):
    try:
        return jsonify(action()), success_status
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@api_bp.get("/health")
def health() -> tuple[dict, int]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_title}, 200


@api_bp.post("/auth/register")
def auth_register():
    payload = request.get_json(silent=True) or {}
    return _respond(lambda: register_user(payload), success_status=201)


@api_bp.post("/auth/login")
def auth_login():
    payload = request.get_json(silent=True) or {}
    return _respond(lambda: login_user(payload))


@api_bp.get("/auth/account/<user_id>")
def auth_account(user_id: str):
    account = get_account(user_id)
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(account)


@api_bp.get("/profile/<user_id>")
def profile(user_id: str):
    return _respond(lambda: get_profile(user_id))


@api_bp.post("/profile")
def profile_update():
    payload = request.get_json(silent=True) or {}
    return _respond(lambda: update_profile(payload))


@api_bp.post("/checkins")
def create_checkin():
    payload = request.get_json(silent=True) or {}
    return _respond(lambda: submit_check_in(payload), success_status=201)


@api_bp.get("/dashboard/<user_id>")
def dashboard(user_id: str):
    days = int(request.args.get("days", "30"))
    return _respond(lambda: get_dashboard(user_id, days=days))


@api_bp.get("/notifications/<user_id>")
def notifications(user_id: str):
    return _respond(lambda: get_notifications(user_id))


@api_bp.get("/alerts/provider-status")
def alerts_provider_status():
    return _respond(get_alert_provider_status)


@api_bp.get("/ml/overview")
def ml_overview():
    return _respond(get_ml_overview)


@api_bp.post("/assistant")
def assistant():
    payload = request.get_json(silent=True) or {}
    return _respond(lambda: support_chat(payload))


@api_bp.get("/resources")
def resources():
    campus = request.args.get("campus", "Main Campus")
    risk_level = request.args.get("risk_level", "Normal")
    return _respond(lambda: get_resources(campus, risk_level))


@api_bp.get("/peer-posts")
def peer_posts():
    return _respond(list_peer_posts)


@api_bp.post("/peer-posts")
def peer_post_create():
    payload = request.get_json(silent=True) or {}
    return _respond(lambda: create_peer_post(payload), success_status=201)


@api_bp.get("/buddy-matches/<user_id>")
def buddy_matches(user_id: str):
    return _respond(lambda: get_buddy_matches(user_id))


@api_bp.get("/admin/overview")
def admin_overview():
    days = int(request.args.get("days", "30"))
    return _respond(lambda: get_admin_overview(days))
