from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from shared.config import get_settings


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


@dataclass
class CheckInPayload:
    user_id: str
    name: str
    course: str
    year: int
    campus: str
    language: str
    anonymous_mode: bool
    consent_alerts: bool
    alert_contact: str
    alert_channel: str
    student_email: str
    phone_number: str
    trusted_contact_email: str
    trusted_contact_phone: str
    mood_label: str
    mood_score: int
    stress_score: int
    energy_score: int
    sleep_hours: float
    attendance_rate: float
    assignments_due: int
    social_connectedness: int
    exam_pressure: int
    notes: str = ""
    log_date: str = field(default_factory=lambda: date.today().isoformat())

    @classmethod
    def from_dict(cls, payload: dict) -> "CheckInPayload":
        settings = get_settings()
        return cls(
            user_id=str(payload.get("user_id") or settings.default_user_id).strip(),
            name=str(payload.get("name") or "Student").strip()[:80],
            course=str(payload.get("course") or "B.Tech CSE").strip()[:80],
            year=int(clamp(float(payload.get("year", 2)), 1, 5)),
            campus=str(payload.get("campus") or settings.default_campus).strip()[:80],
            language=str(payload.get("language") or settings.default_language).strip()[:30],
            anonymous_mode=bool(payload.get("anonymous_mode", False)),
            consent_alerts=bool(payload.get("consent_alerts", False)),
            alert_contact=str(payload.get("alert_contact") or "").strip()[:80],
            alert_channel=str(payload.get("alert_channel") or "Mentor").strip()[:40],
            student_email=str(payload.get("student_email") or "").strip()[:120],
            phone_number=str(payload.get("phone_number") or "").strip()[:20],
            trusted_contact_email=str(payload.get("trusted_contact_email") or "").strip()[:120],
            trusted_contact_phone=str(payload.get("trusted_contact_phone") or "").strip()[:20],
            mood_label=str(payload.get("mood_label") or "Okay").strip()[:40],
            mood_score=int(clamp(float(payload.get("mood_score", 3)), 1, 5)),
            stress_score=int(clamp(float(payload.get("stress_score", 5)), 1, 10)),
            energy_score=int(clamp(float(payload.get("energy_score", 5)), 1, 10)),
            sleep_hours=float(clamp(float(payload.get("sleep_hours", 7)), 0, 14)),
            attendance_rate=float(clamp(float(payload.get("attendance_rate", 85)), 0, 100)),
            assignments_due=int(clamp(float(payload.get("assignments_due", 1)), 0, 20)),
            social_connectedness=int(
                clamp(float(payload.get("social_connectedness", 3)), 1, 5)
            ),
            exam_pressure=int(clamp(float(payload.get("exam_pressure", 5)), 1, 10)),
            notes=str(payload.get("notes") or "").strip()[:1000],
            log_date=str(payload.get("log_date") or date.today().isoformat()),
        )


@dataclass
class SupportRequest:
    user_id: str
    message: str
    language: str

    @classmethod
    def from_dict(cls, payload: dict) -> "SupportRequest":
        settings = get_settings()
        return cls(
            user_id=str(payload.get("user_id") or settings.default_user_id).strip(),
            message=str(payload.get("message") or "").strip()[:1000],
            language=str(payload.get("language") or settings.default_language).strip()[:30],
        )


@dataclass
class PeerPostPayload:
    alias: str
    topic: str
    message: str

    @classmethod
    def from_dict(cls, payload: dict) -> "PeerPostPayload":
        return cls(
            alias=str(payload.get("alias") or "Anonymous").strip()[:50],
            topic=str(payload.get("topic") or "Daily Win").strip()[:60],
            message=str(payload.get("message") or "").strip()[:400],
        )


@dataclass
class RegistrationPayload:
    name: str
    email: str
    password: str
    confirm_password: str
    course: str
    year: int
    campus: str
    language: str
    phone_number: str

    @classmethod
    def from_dict(cls, payload: dict) -> "RegistrationPayload":
        settings = get_settings()
        return cls(
            name=str(payload.get("name") or "Student").strip()[:80],
            email=str(payload.get("email") or "").strip()[:120],
            password=str(payload.get("password") or ""),
            confirm_password=str(payload.get("confirm_password") or payload.get("password") or ""),
            course=str(payload.get("course") or "B.Tech CSE").strip()[:80],
            year=int(clamp(float(payload.get("year", 2)), 1, 5)),
            campus=str(payload.get("campus") or settings.default_campus).strip()[:80],
            language=str(payload.get("language") or settings.default_language).strip()[:30],
            phone_number=str(payload.get("phone_number") or "").strip()[:20],
        )


@dataclass
class LoginPayload:
    email: str
    password: str

    @classmethod
    def from_dict(cls, payload: dict) -> "LoginPayload":
        return cls(
            email=str(payload.get("email") or "").strip()[:120],
            password=str(payload.get("password") or ""),
        )
