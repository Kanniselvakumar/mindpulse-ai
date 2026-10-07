from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

from backend.data.seed import (
    seed_academic_calendar,
    seed_coping_plans,
    seed_demo_cohort,
    seed_demo_user,
    seed_peer_circles,
    seed_peer_posts,
)
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
    seed_academic_calendar()
    seed_coping_plans(get_settings().default_user_id)
    seed_peer_circles()
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


# ─── Academic Calendar ────────────────────────────────────────────────────────

def get_upcoming_events(days_ahead: int = 14) -> list[dict[str, Any]]:
    """Return academic calendar events in the next `days_ahead` days, ordered by date."""
    bootstrap()
    from datetime import date, timedelta
    today = date.today().isoformat()
    cutoff = (date.today() + timedelta(days=days_ahead)).isoformat()
    return fetch_all(
        "SELECT * FROM academic_calendar WHERE event_date BETWEEN ? AND ? ORDER BY event_date ASC",
        (today, cutoff),
    )


# ─── Coping Plans ─────────────────────────────────────────────────────────────

def get_coping_plan(user_id: str) -> list[dict[str, Any]]:
    """Return the current week's coping plan items for a user."""
    bootstrap()
    from datetime import date
    today = date.today().isoformat()
    plans = fetch_all(
        "SELECT * FROM coping_plans WHERE user_id = ? AND plan_date = ? ORDER BY id ASC",
        (user_id, today),
    )
    # If no plan for today, return a fresh set seeded from stored strategies
    if not plans:
        seed_coping_plans(user_id)
        plans = fetch_all(
            "SELECT * FROM coping_plans WHERE user_id = ? AND plan_date = ? ORDER BY id ASC",
            (user_id, today),
        )
    return plans


def update_coping_plan_item(plan_id: int, completed: bool, feedback: str = "") -> dict[str, Any]:
    """Mark a coping plan item completed and store feedback."""
    execute(
        "UPDATE coping_plans SET completed = ?, feedback = ? WHERE id = ?",
        (int(completed), feedback, plan_id),
    )
    return fetch_one("SELECT * FROM coping_plans WHERE id = ?", (plan_id,)) or {}


# ─── Appointments ─────────────────────────────────────────────────────────────

def request_appointment(student_id: str, slot_time: str, reason: str = "") -> dict[str, Any]:
    """Student requests a counselor session slot."""
    bootstrap()
    from datetime import datetime
    created_at = datetime.utcnow().replace(microsecond=0).isoformat()
    appt_id = execute(
        """
        INSERT INTO appointments (student_id, counselor_id, slot_time, reason, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (student_id, "counselor-admin", slot_time, reason, "pending", created_at),
    )
    return {"id": appt_id, "status": "pending", "slot_time": slot_time, "reason": reason}


def get_appointments(user_id: str, role: str = "student") -> list[dict[str, Any]]:
    """Fetch appointments for a student or counselor."""
    bootstrap()
    if role == "counselor":
        return fetch_all(
            "SELECT * FROM appointments ORDER BY slot_time ASC"
        )
    return fetch_all(
        "SELECT * FROM appointments WHERE student_id = ? ORDER BY slot_time ASC",
        (user_id,),
    )


def update_appointment_status(appt_id: int, status: str, notes: str = "") -> dict[str, Any]:
    """Counselor confirms, completes or cancels an appointment."""
    execute(
        "UPDATE appointments SET status = ?, notes = ? WHERE id = ?",
        (status, notes, appt_id),
    )
    return fetch_one("SELECT * FROM appointments WHERE id = ?", (appt_id,)) or {}


# ─── Peer Circles ─────────────────────────────────────────────────────────────

def get_peer_circles() -> list[dict[str, Any]]:
    """Return all available peer support circles."""
    bootstrap()
    return fetch_all("SELECT * FROM peer_circles ORDER BY id ASC")


def join_peer_circle(circle_id: int, user_id: str) -> dict[str, Any]:
    """Add a user to a peer circle's members list."""
    import json
    circle = fetch_one("SELECT * FROM peer_circles WHERE id = ?", (circle_id,))
    if not circle:
        return {"error": "Circle not found"}
    members = json.loads(circle.get("members", "[]"))
    if user_id not in members:
        members.append(user_id)
        execute(
            "UPDATE peer_circles SET members = ? WHERE id = ?",
            (json.dumps(members), circle_id),
        )
    return fetch_one("SELECT * FROM peer_circles WHERE id = ?", (circle_id,)) or {}


# ─── Cohort Analytics ─────────────────────────────────────────────────────────

def get_cohort_overview(days: int = 30) -> dict[str, Any]:
    """Return department-wise and year-wise stress heatmap data for counselors."""
    import pandas as pd
    frame = _logs_frame(None, days=days)
    if frame.empty:
        return {"department_heatmap": [], "year_heatmap": [], "privacy_note": "No data yet."}

    profiles = pd.DataFrame(
        fetch_all("SELECT user_id, course, year, campus FROM user_profiles")
    )
    merged = frame.merge(profiles, on="user_id", how="left")

    dept_heatmap = (
        merged.groupby("course")
        .agg(
            avg_stress=("stress_score", "mean"),
            avg_mood=("mood_score", "mean"),
            high_risk_count=("risk_level", lambda x: (x == "High Risk").sum()),
            student_count=("user_id", "nunique"),
        )
        .reset_index()
        .rename(columns={"course": "department"})
    )
    dept_heatmap["avg_stress"] = dept_heatmap["avg_stress"].round(2)
    dept_heatmap["avg_mood"] = dept_heatmap["avg_mood"].round(2)

    year_heatmap = (
        merged.groupby("year")
        .agg(
            avg_stress=("stress_score", "mean"),
            avg_mood=("mood_score", "mean"),
            high_risk_count=("risk_level", lambda x: (x == "High Risk").sum()),
        )
        .reset_index()
    )
    year_heatmap["avg_stress"] = year_heatmap["avg_stress"].round(2)
    year_heatmap["avg_mood"] = year_heatmap["avg_mood"].round(2)

    return {
        "department_heatmap": dept_heatmap.to_dict(orient="records"),
        "year_heatmap": year_heatmap.to_dict(orient="records"),
        "privacy_note": "Only aggregate, anonymized data is shown. No individual records are exposed.",
    }


def parse_dataset_input(file_content: str | bytes, filename: str) -> pd.DataFrame:
    import io
    if isinstance(file_content, bytes):
        raw_bytes = file_content
    else:
        raw_bytes = file_content.encode("utf-8")

    if filename.endswith(".json"):
        return pd.read_json(io.BytesIO(raw_bytes))
    else:
        return pd.read_csv(io.BytesIO(raw_bytes))


def upload_and_evaluate_dataset(file_content: str | bytes, filename: str) -> dict[str, Any]:
    df = parse_dataset_input(file_content, filename)
    cleaned_df, profile = risk_engine.process_and_validate_dataset(df)
    return {
        "filename": filename,
        "profile": profile,
        "preview": cleaned_df.head(10).to_dict(orient="records"),
    }


def retrain_model_with_custom_dataset(file_content: str | bytes, filename: str) -> dict[str, Any]:
    df = parse_dataset_input(file_content, filename)
    retrain_result = risk_engine.retrain_with_custom_dataset(df, dataset_name=filename)
    return retrain_result


def predict_realtime_sample(sample_dict: dict[str, Any]) -> dict[str, Any]:
    return risk_engine.predict_single_sample(sample_dict)


def get_sample_wellness_csv() -> str:
    return risk_engine.generate_sample_wellness_csv()

