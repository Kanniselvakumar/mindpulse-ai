from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data"


@dataclass(frozen=True)
class Settings:
    app_title: str
    environment: str
    secret_key: str
    api_base_url: str
    force_local_backend: bool
    database_path: Path
    default_user_id: str
    default_language: str
    default_campus: str
    real_alert_delivery_enabled: bool
    alert_email_provider: str
    alert_sms_provider: str
    alert_email_from: str
    alert_email_reply_to: str
    resend_api_key: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_number: str
    twilio_messaging_service_sid: str

    @property
    def fernet_key(self) -> bytes:
        raw_key = os.getenv("FERNET_KEY")
        if raw_key:
            return raw_key.encode("utf-8")

        digest = hashlib.sha256(self.secret_key.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_title="MindPulse AI",
        environment=os.getenv("APP_ENV", "local"),
        secret_key=os.getenv("APP_SECRET_KEY", "student-wellness-demo-secret"),
        api_base_url=os.getenv("API_BASE_URL", "").rstrip("/"),
        force_local_backend=os.getenv("STREAMLIT_FORCE_LOCAL_BACKEND", "true").lower()
        == "true",
        database_path=Path(os.getenv("DATABASE_PATH", DATA_DIR / "wellness.db")),
        default_user_id=os.getenv("DEFAULT_USER_ID", "demo-student"),
        default_language=os.getenv("DEFAULT_LANGUAGE", "English"),
        default_campus=os.getenv("DEFAULT_CAMPUS", "Main Campus"),
        real_alert_delivery_enabled=os.getenv("ALERT_REAL_DELIVERY_ENABLED", "false").lower()
        == "true",
        alert_email_provider=os.getenv("ALERT_EMAIL_PROVIDER", "resend").strip().lower(),
        alert_sms_provider=os.getenv("ALERT_SMS_PROVIDER", "twilio").strip().lower(),
        alert_email_from=os.getenv("ALERT_EMAIL_FROM", "").strip(),
        alert_email_reply_to=os.getenv("ALERT_EMAIL_REPLY_TO", "").strip(),
        resend_api_key=os.getenv("RESEND_API_KEY", "").strip(),
        twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID", "").strip(),
        twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", "").strip(),
        twilio_from_number=os.getenv("TWILIO_FROM_NUMBER", "").strip(),
        twilio_messaging_service_sid=os.getenv("TWILIO_MESSAGING_SERVICE_SID", "").strip(),
    )


def ensure_app_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
