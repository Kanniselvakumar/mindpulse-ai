from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

from shared.config import ensure_app_directories, get_settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    course TEXT NOT NULL,
    year INTEGER NOT NULL,
    campus TEXT NOT NULL,
    language TEXT NOT NULL,
    anonymous_mode INTEGER NOT NULL DEFAULT 0,
    consent_alerts INTEGER NOT NULL DEFAULT 0,
    alert_contact TEXT DEFAULT '',
    alert_channel TEXT DEFAULT 'Mentor',
    preferred_checkin_time TEXT DEFAULT '20:00',
    student_email TEXT DEFAULT '',
    phone_number TEXT DEFAULT '',
    trusted_contact_email TEXT DEFAULT '',
    trusted_contact_phone TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_accounts (
    user_id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student',
    is_active INTEGER NOT NULL DEFAULT 1,
    phone_number TEXT DEFAULT '',
    last_login_at TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mood_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    log_date TEXT NOT NULL,
    mood_label TEXT NOT NULL,
    mood_score INTEGER NOT NULL,
    stress_score INTEGER NOT NULL,
    energy_score INTEGER NOT NULL,
    sleep_hours REAL NOT NULL,
    attendance_rate REAL NOT NULL,
    assignments_due INTEGER NOT NULL,
    social_connectedness INTEGER NOT NULL,
    exam_pressure INTEGER NOT NULL,
    notes TEXT DEFAULT '',
    sentiment REAL NOT NULL,
    subjectivity REAL NOT NULL,
    emotion TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    risk_score REAL NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alert_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    log_id INTEGER,
    risk_level TEXT NOT NULL,
    message TEXT NOT NULL,
    contact_name TEXT DEFAULT '',
    triggered INTEGER NOT NULL DEFAULT 0,
    email_status TEXT DEFAULT 'not_requested',
    sms_status TEXT DEFAULT 'not_requested',
    email_provider_id TEXT DEFAULT '',
    sms_provider_id TEXT DEFAULT '',
    delivery_error TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS peer_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias TEXT NOT NULL,
    topic TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

MIGRATIONS = {
    "user_profiles": {
        "student_email": "TEXT DEFAULT ''",
        "phone_number": "TEXT DEFAULT ''",
        "trusted_contact_email": "TEXT DEFAULT ''",
        "trusted_contact_phone": "TEXT DEFAULT ''",
    },
    "alert_events": {
        "email_status": "TEXT DEFAULT 'not_requested'",
        "sms_status": "TEXT DEFAULT 'not_requested'",
        "email_provider_id": "TEXT DEFAULT ''",
        "sms_provider_id": "TEXT DEFAULT ''",
        "delivery_error": "TEXT DEFAULT ''",
    },
}


def dict_from_row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def _apply_migrations(connection: sqlite3.Connection) -> None:
    for table_name, columns in MIGRATIONS.items():
        existing = _table_columns(connection, table_name)
        for column_name, definition in columns.items():
            if column_name not in existing:
                connection.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"
                )


def init_db() -> None:
    ensure_app_directories()
    with get_connection() as connection:
        connection.executescript(SCHEMA)
        _apply_migrations(connection)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    settings = get_settings()
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def fetch_one(query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(query, params).fetchone()
    return dict_from_row(row)


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict_from_row(row) for row in rows if row is not None]


def execute(query: str, params: tuple[Any, ...] = ()) -> int:
    with get_connection() as connection:
        cursor = connection.execute(query, params)
        return int(cursor.lastrowid)
