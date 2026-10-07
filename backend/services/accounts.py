from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from werkzeug.security import check_password_hash, generate_password_hash

from backend.database import execute, fetch_one
from shared.config import get_settings


def _timestamp() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def normalize_email(value: str) -> str:
    return value.strip().lower()


def _boolify_profile(profile: dict[str, Any]) -> dict[str, Any]:
    hydrated = dict(profile)
    hydrated["anonymous_mode"] = bool(hydrated.get("anonymous_mode", 0))
    hydrated["consent_alerts"] = bool(hydrated.get("consent_alerts", 0))
    return hydrated


def _boolify_account(account: dict[str, Any]) -> dict[str, Any]:
    hydrated = dict(account)
    hydrated["is_active"] = bool(hydrated.get("is_active", 0))
    return hydrated


def default_profile(user_id: str) -> dict[str, Any]:
    settings = get_settings()
    return {
        "user_id": user_id,
        "name": "Student",
        "course": "B.Tech CSE",
        "year": 2,
        "campus": settings.default_campus,
        "language": settings.default_language,
        "anonymous_mode": False,
        "consent_alerts": False,
        "alert_contact": "",
        "alert_channel": "Mentor",
        "preferred_checkin_time": "20:00",
        "student_email": "",
        "phone_number": "",
        "trusted_contact_email": "",
        "trusted_contact_phone": "",
    }


def get_profile(user_id: str, autocreate: bool = True) -> dict[str, Any] | None:
    profile = fetch_one("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
    if profile:
        return _boolify_profile(profile)
    if not autocreate:
        return None
    upsert_profile(default_profile(user_id))
    return get_profile(user_id, autocreate=False)


def upsert_profile(profile: dict[str, Any]) -> None:
    now = _timestamp()
    merged = {**default_profile(str(profile["user_id"])), **profile}
    existing = fetch_one("SELECT user_id FROM user_profiles WHERE user_id = ?", (merged["user_id"],))

    update_params = (
        merged["name"],
        merged["course"],
        int(merged["year"]),
        merged["campus"],
        merged["language"],
        int(bool(merged.get("anonymous_mode", False))),
        int(bool(merged.get("consent_alerts", False))),
        merged.get("alert_contact", ""),
        merged.get("alert_channel", "Mentor"),
        merged.get("preferred_checkin_time", "20:00"),
        merged.get("student_email", ""),
        merged.get("phone_number", ""),
        merged.get("trusted_contact_email", ""),
        merged.get("trusted_contact_phone", ""),
        now,
        merged["user_id"],
    )
    insert_params = (
        merged["user_id"],
        merged["name"],
        merged["course"],
        int(merged["year"]),
        merged["campus"],
        merged["language"],
        int(bool(merged.get("anonymous_mode", False))),
        int(bool(merged.get("consent_alerts", False))),
        merged.get("alert_contact", ""),
        merged.get("alert_channel", "Mentor"),
        merged.get("preferred_checkin_time", "20:00"),
        merged.get("student_email", ""),
        merged.get("phone_number", ""),
        merged.get("trusted_contact_email", ""),
        merged.get("trusted_contact_phone", ""),
        now,
        now,
    )

    if existing:
        execute(
            """
            UPDATE user_profiles
            SET name = ?, course = ?, year = ?, campus = ?, language = ?,
                anonymous_mode = ?, consent_alerts = ?, alert_contact = ?,
                alert_channel = ?, preferred_checkin_time = ?, student_email = ?,
                phone_number = ?, trusted_contact_email = ?, trusted_contact_phone = ?,
                updated_at = ?
            WHERE user_id = ?
            """,
            update_params,
        )
    else:
        execute(
            """
            INSERT INTO user_profiles (
                user_id, name, course, year, campus, language, anonymous_mode,
                consent_alerts, alert_contact, alert_channel, preferred_checkin_time,
                student_email, phone_number, trusted_contact_email, trusted_contact_phone,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            insert_params,
        )

    execute(
        "UPDATE user_accounts SET phone_number = ?, updated_at = ? WHERE user_id = ?",
        (merged.get("phone_number", ""), now, merged["user_id"]),
    )


def get_account_by_user_id(user_id: str) -> dict[str, Any] | None:
    row = fetch_one("SELECT * FROM user_accounts WHERE user_id = ?", (user_id,))
    if not row:
        return None
    account = _boolify_account(row)
    account["profile"] = get_profile(user_id)
    return account


def get_account_by_email(email: str) -> dict[str, Any] | None:
    row = fetch_one("SELECT * FROM user_accounts WHERE email = ?", (normalize_email(email),))
    if not row:
        return None
    account = _boolify_account(row)
    account["profile"] = get_profile(account["user_id"])
    return account


def seed_account(
    user_id: str,
    email: str,
    password: str,
    role: str = "student",
    phone_number: str = "",
) -> None:
    email = normalize_email(email)
    now = _timestamp()
    existing = fetch_one("SELECT user_id FROM user_accounts WHERE email = ?", (email,))
    if existing:
        return
    execute(
        """
        INSERT INTO user_accounts (
            user_id, email, password_hash, role, is_active, phone_number,
            last_login_at, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            email,
            generate_password_hash(password),
            role,
            1,
            phone_number,
            "",
            now,
            now,
        ),
    )


def register_account(payload: dict[str, Any]) -> dict[str, Any]:
    email = normalize_email(str(payload.get("email") or ""))
    password = str(payload.get("password") or "")
    confirm_password = str(payload.get("confirm_password") or password)
    if not email or "@" not in email:
        raise ValueError("Enter a valid email address.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if password != confirm_password:
        raise ValueError("Password and confirm password do not match.")
    if get_account_by_email(email):
        raise ValueError("An account with this email already exists.")

    user_id = f"user-{uuid.uuid4().hex[:12]}"
    phone_number = str(payload.get("phone_number") or "").strip()[:20]
    seed_account(user_id, email, password, role="student", phone_number=phone_number)
    upsert_profile(
        {
            "user_id": user_id,
            "name": str(payload.get("name") or "Student").strip()[:80],
            "course": str(payload.get("course") or "B.Tech CSE").strip()[:80],
            "year": int(float(payload.get("year", 2))),
            "campus": str(payload.get("campus") or get_settings().default_campus).strip()[:80],
            "language": str(payload.get("language") or get_settings().default_language).strip()[:30],
            "student_email": email,
            "phone_number": phone_number,
        }
    )
    account = get_account_by_user_id(user_id)
    if not account:
        raise ValueError("Account could not be created.")
    return account


def authenticate_account(email: str, password: str) -> dict[str, Any]:
    email = normalize_email(email)
    row = fetch_one("SELECT * FROM user_accounts WHERE email = ?", (email,))
    if not row or not bool(row["is_active"]):
        raise ValueError("Invalid email or password.")
    if not check_password_hash(row["password_hash"], password):
        raise ValueError("Invalid email or password.")

    now = _timestamp()
    execute(
        "UPDATE user_accounts SET last_login_at = ?, updated_at = ? WHERE user_id = ?",
        (now, now, row["user_id"]),
    )
    account = get_account_by_user_id(row["user_id"])
    if not account:
        raise ValueError("Unable to load the account after login.")
    return account
