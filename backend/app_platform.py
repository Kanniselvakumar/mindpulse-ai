from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

from backend.data.seed import seed_demo_cohort, seed_demo_user, seed_peer_posts
from backend.database import execute, fetch_all, fetch_one, init_db
from backend.models.payloads import (
    CheckInPayload,
    LoginPayload,
    PeerPostPayload,
    RegistrationPayload,
    SupportRequest,
)
from backend.services.accounts import (
    authenticate_account,
    get_account_by_user_id,
    get_profile as get_profile_record,
    register_account,
    seed_account,
    upsert_profile,
)
from backend.services.alerts import dispatch_high_risk_alert, get_provider_status
from backend.services.analytics import build_dashboard
from backend.services.assistant import build_support_reply
from backend.services.nlp_engine import analyze_text
from backend.services.peer_support import suggest_buddies
from backend.services.recommendations import build_recommendations
from backend.services.resources import get_resource_pack
from backend.services.risk_engine import risk_engine
from backend.services.security import decrypt_text, encrypt_text
from shared.config import get_settings


_BOOTSTRAPPED = False


def _timestamp() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def _seed_demo_accounts() -> None:
    settings = get_settings()
    student_email = "demo@studentwellness.local"
    counselor_email = "counselor@studentwellness.local"

    upsert_profile(
        {
            "user_id": settings.default_user_id,
            "name": "Demo Student",
            "course": "B.Tech CSE",
            "year": 2,
            "campus": settings.default_campus,
            "language": settings.default_language,
            "consent_alerts": True,
            "alert_contact": "Faculty Mentor",
            "alert_channel": "Mentor",
            "student_email": student_email,
            "phone_number": "",
            "trusted_contact_email": "",
            "trusted_contact_phone": "",
        }
    )
    seed_account(
        settings.default_user_id,
        student_email,
        "Demo@12345",
        role="student",
    )

    upsert_profile(
        {
            "user_id": "counselor-admin",
            "name": "Counselor Admin",
            "course": "Student Support Services",
            "year": 1,
            "campus": settings.default_campus,
            "language": settings.default_language,
            "student_email": counselor_email,
        }
    )
    seed_account(
        "counselor-admin",
        counselor_email,
        "Counselor@123",
        role="counselor",
    )


def bootstrap() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return

    init_db()
    _seed_demo_accounts()
    seed_peer_posts()
    seed_demo_user(get_settings().default_user_id)
    seed_demo_cohort()
    _BOOTSTRAPPED = True


def register_user(payload: dict[str, Any]) -> dict[str, Any]:
    bootstrap()
    request = RegistrationPayload.from_dict(payload)
    return register_account(vars(request))


def login_user(payload: dict[str, Any]) -> dict[str, Any]:
    bootstrap()
    request = LoginPayload.from_dict(payload)
    return authenticate_account(request.email, request.password)


def get_account(user_id: str) -> dict[str, Any] | None:
    bootstrap()
    return get_account_by_user_id(user_id)


def get_profile(user_id: str) -> dict[str, Any]:
    bootstrap()
    profile = get_profile_record(user_id)
    if not profile:
        raise ValueError("Profile not found.")
    return profile


def update_profile(payload: dict[str, Any]) -> dict[str, Any]:
    bootstrap()
    user_id = str(payload.get("user_id") or "").strip()
    if not user_id:
        raise ValueError("user_id is required to update the profile.")
    existing = get_profile_record(user_id) or {"user_id": user_id}
    merged = {**existing, **payload}
    account = get_account_by_user_id(user_id)
    if account and not merged.get("student_email"):
        merged["student_email"] = account["email"]
    upsert_profile(merged)
    profile = get_profile_record(user_id)
    if not profile:
        raise ValueError("Profile could not be updated.")
    return profile


def _logs_frame(user_id: str | None = None, days: int = 30) -> pd.DataFrame:
    bootstrap()
    if user_id:
        rows = fetch_all(
            "SELECT * FROM mood_logs WHERE user_id = ? ORDER BY log_date ASC",
            (user_id,),
        )
    else:
        rows = fetch_all("SELECT * FROM mood_logs ORDER BY log_date ASC")

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame

    frame["log_date"] = pd.to_datetime(frame["log_date"])
    if days > 0:
        cutoff = pd.Timestamp(date.today() - timedelta(days=days - 1))
        frame = frame[frame["log_date"] >= cutoff]
    frame = frame.sort_values("log_date")
    return frame


def submit_check_in(payload: dict[str, Any]) -> dict[str, Any]:
    bootstrap()
    checkin = CheckInPayload.from_dict(payload)
    upsert_profile(
        {
            "user_id": checkin.user_id,
            "name": "Anonymous Student" if checkin.anonymous_mode else checkin.name,
            "course": checkin.course,
            "year": checkin.year,
            "campus": checkin.campus,
            "language": checkin.language,
            "anonymous_mode": checkin.anonymous_mode,
            "consent_alerts": checkin.consent_alerts,
            "alert_contact": checkin.alert_contact,
            "alert_channel": checkin.alert_channel,
            "student_email": checkin.student_email,
            "phone_number": checkin.phone_number,
            "trusted_contact_email": checkin.trusted_contact_email,
            "trusted_contact_phone": checkin.trusted_contact_phone,
        }
    )

    recent_logs = _logs_frame(checkin.user_id, days=30)
    analysis = analyze_text(checkin.notes)
    risk = risk_engine.predict(checkin, analysis, recent_logs)

    log_id = execute(
        """
        INSERT INTO mood_logs (
            user_id, log_date, mood_label, mood_score, stress_score, energy_score,
            sleep_hours, attendance_rate, assignments_due, social_connectedness,
            exam_pressure, notes, sentiment, subjectivity, emotion, risk_level,
            risk_score, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            checkin.user_id,
            checkin.log_date,
            checkin.mood_label,
            checkin.mood_score,
            checkin.stress_score,
            checkin.energy_score,
            checkin.sleep_hours,
            checkin.attendance_rate,
            checkin.assignments_due,
            checkin.social_connectedness,
            checkin.exam_pressure,
            encrypt_text(checkin.notes),
            analysis["polarity"],
            analysis["subjectivity"],
            analysis["emotion"],
            risk["label"],
            risk["risk_score"],
            _timestamp(),
        ),
    )

    dashboard = get_dashboard(checkin.user_id, days=30)
    recommendations = build_recommendations(
        checkin,
        analysis,
        risk,
        streak=dashboard["metrics"]["check_in_streak"],
    )

    alert = None
    if risk["label"] == "High Risk":
        alert_message = (
            "A high-risk wellness pattern was detected. Please reach out, offer support, and encourage professional help if needed."
        )
        profile = get_profile(checkin.user_id)
        triggered = bool(checkin.consent_alerts)
        if triggered:
            delivery = dispatch_high_risk_alert(profile, alert_message)
        else:
            delivery = {
                "contact_name": profile.get("alert_contact") or "Trusted contact",
                "email": {
                    "channel": "email",
                    "status": "consent_not_granted",
                    "provider": "",
                    "provider_id": "",
                    "error": "Consent-based alerts are disabled for this profile.",
                    "recipient": profile.get("trusted_contact_email", ""),
                },
                "sms": {
                    "channel": "sms",
                    "status": "consent_not_granted",
                    "provider": "",
                    "provider_id": "",
                    "error": "Consent-based alerts are disabled for this profile.",
                    "recipient": profile.get("trusted_contact_phone", ""),
                },
                "provider_status": get_provider_status(),
                "message": alert_message,
            }

        execute(
            """
            INSERT INTO alert_events (
                user_id, log_id, risk_level, message, contact_name, triggered,
                email_status, sms_status, email_provider_id, sms_provider_id,
                delivery_error, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                checkin.user_id,
                log_id,
                risk["label"],
                alert_message,
                delivery["contact_name"],
                int(triggered),
                delivery["email"]["status"],
                delivery["sms"]["status"],
                delivery["email"]["provider_id"],
                delivery["sms"]["provider_id"],
                " | ".join(
                    [item for item in [delivery["email"]["error"], delivery["sms"]["error"]] if item]
                ),
                _timestamp(),
            ),
        )
        alert = {
            "triggered": triggered,
            "contact_name": delivery["contact_name"] or "No contact selected",
            "message": alert_message,
            "delivery": delivery,
        }

    return {
        "checkin_id": log_id,
        "analysis": analysis,
        "risk": risk,
        "recommendations": recommendations,
        "alert": alert,
        "dashboard": dashboard,
    }


def get_dashboard(user_id: str, days: int = 30) -> dict[str, Any]:
    frame = _logs_frame(user_id, days)
    dashboard = build_dashboard(frame)
    if dashboard["latest_entry"]:
        latest_notes = fetch_one(
            """
            SELECT notes
            FROM mood_logs
            WHERE user_id = ?
            ORDER BY log_date DESC, id DESC
            LIMIT 1
            """,
            (user_id,),
        )
        dashboard["latest_entry"]["notes"] = decrypt_text((latest_notes or {}).get("notes", ""))
    dashboard["profile"] = get_profile(user_id)
    dashboard["notifications"] = get_notifications(user_id)
    dashboard["provider_status"] = get_provider_status()
    return dashboard


def get_notifications(user_id: str) -> list[dict[str, Any]]:
    profile = get_profile(user_id)
    frame = _logs_frame(user_id, days=90)
    notes: list[dict[str, Any]] = []

    if frame.empty:
        notes.append(
            {
                "level": "info",
                "title": "First Check-in",
                "message": "Start with a quick emoji check-in to unlock your dashboard insights.",
            }
        )
        return notes

    latest = frame.iloc[-1]
    days_since = (date.today() - latest["log_date"].date()).days
    if days_since >= 3:
        notes.append(
            {
                "level": "warning",
                "title": "Missed Check-ins",
                "message": f"You have not checked in for {days_since} days. A 20-second update can help.",
            }
        )
    if latest["risk_level"] == "High Risk":
        notes.append(
            {
                "level": "error",
                "title": "Human Support Recommended",
                "message": "Please connect with a mentor, counselor, or helpline today.",
            }
        )
    if frame.tail(7)["mood_score"].mean() >= 3.8:
        notes.append(
            {
                "level": "success",
                "title": "Positive Momentum",
                "message": "Your recent check-ins show a stronger mood pattern. Keep repeating what helps.",
            }
        )
    if profile.get("consent_alerts") and (
        profile.get("trusted_contact_email") or profile.get("trusted_contact_phone")
    ):
        notes.append(
            {
                "level": "info",
                "title": "Trusted Contact Ready",
                "message": "Consent-based trusted contact delivery is configured for this profile.",
            }
        )
    provider_status = get_provider_status()
    if not provider_status["real_delivery_enabled"]:
        notes.append(
            {
                "level": "warning",
                "title": "Alerts in Safe Mode",
                "message": "Provider calls are disabled until ALERT_REAL_DELIVERY_ENABLED=true.",
            }
        )
    return notes


def support_chat(payload: dict[str, Any]) -> dict[str, Any]:
    request = SupportRequest.from_dict(payload)
    dashboard = get_dashboard(request.user_id, days=14)
    latest_snapshot = dashboard.get("latest_entry")
    response = build_support_reply(request.message, latest_snapshot, request.language)
    response["latest_risk_level"] = (latest_snapshot or {}).get("risk_level", "Normal")
    return response


def get_resources(campus: str, risk_level: str = "Normal") -> dict[str, Any]:
    return get_resource_pack(campus, risk_level)


def get_alert_provider_status() -> dict[str, Any]:
    bootstrap()
    return get_provider_status()


def get_ml_overview() -> dict[str, Any]:
    bootstrap()
    return risk_engine.describe_model()


def list_peer_posts() -> list[dict[str, Any]]:
    bootstrap()
    return fetch_all("SELECT * FROM peer_posts ORDER BY id DESC LIMIT 20")


def create_peer_post(payload: dict[str, Any]) -> dict[str, Any]:
    bootstrap()
    post = PeerPostPayload.from_dict(payload)
    post_id = execute(
        """
        INSERT INTO peer_posts (alias, topic, message, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (post.alias, post.topic, post.message, _timestamp()),
    )
    return {
        "id": post_id,
        "alias": post.alias,
        "topic": post.topic,
        "message": post.message,
    }


def get_buddy_matches(user_id: str) -> list[dict[str, Any]]:
    profile = get_profile(user_id)
    return suggest_buddies(profile)


def get_admin_overview(days: int = 30) -> dict[str, Any]:
    frame = _logs_frame(None, days=days)
    if frame.empty:
        return {
            "overall_metrics": {
                "active_students": 0,
                "average_mood": 0.0,
                "average_stress": 0.0,
                "high_risk_students": 0,
            },
            "course_distribution": [],
            "risk_distribution": [],
            "timeline": [],
            "privacy_note": "Only aggregate data is shown here.",
        }

    profiles = pd.DataFrame(
        fetch_all("SELECT user_id, course, year, campus FROM user_profiles")
    )
    merged = frame.merge(profiles, on="user_id", how="left")
    merged["log_date"] = pd.to_datetime(merged["log_date"])

    overall_metrics = {
        "active_students": int(merged["user_id"].nunique()),
        "average_mood": round(float(merged["mood_score"].mean()), 2),
        "average_stress": round(float(merged["stress_score"].mean()), 2),
        "high_risk_students": int(
            merged.loc[merged["risk_level"] == "High Risk", "user_id"].nunique()
        ),
    }
    course_distribution = (
        merged["course"]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("course")
        .reset_index(name="count")
    )
    risk_distribution = (
        merged["risk_level"].value_counts().rename_axis("risk_level").reset_index(name="count")
    )
    timeline = (
        merged.groupby(merged["log_date"].dt.date)
        .agg(average_mood=("mood_score", "mean"), average_stress=("stress_score", "mean"))
        .reset_index()
    )
    timeline["log_date"] = timeline["log_date"].astype(str)

    return {
        "overall_metrics": overall_metrics,
        "course_distribution": course_distribution.to_dict(orient="records"),
        "risk_distribution": risk_distribution.to_dict(orient="records"),
        "timeline": timeline.to_dict(orient="records"),
        "privacy_note": "Only anonymized, aggregate trends are shown. Individual journals stay private.",
    }
