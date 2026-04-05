from __future__ import annotations

from datetime import date, timedelta

from backend.database import execute, fetch_one
from backend.services.security import encrypt_text


DEMO_POSTS = [
    (
        "Anonymous Sparrow",
        "Recovery Story",
        "I started doing 5-minute night check-ins and it actually helped me notice my stress before it became panic.",
    ),
    (
        "CodeBuddy",
        "Study Tip",
        "Pomodoro with a friend on call kept me from doom scrolling before exams.",
    ),
    (
        "Library Owl",
        "Daily Win",
        "Today was rough, but I still attended class and ate on time. Small wins count.",
    ),
]

COHORT_PROFILES = [
    ("cohort-ananya", "Ananya", "B.Tech IT", 3, "Chennai"),
    ("cohort-rohan", "Rohan", "B.Com", 2, "Main Campus"),
    ("cohort-meera", "Meera", "B.Sc Psychology", 3, "Coimbatore"),
    ("cohort-arjun", "Arjun", "B.Tech CSE", 4, "Main Campus"),
]


def _insert_profile(user_id: str, name: str, course: str, year: int, campus: str) -> None:
    existing = fetch_one("SELECT user_id FROM user_profiles WHERE user_id = ?", (user_id,))
    if existing:
        return

    today = date.today().isoformat()
    execute(
        """
        INSERT INTO user_profiles (
            user_id, name, course, year, campus, language, anonymous_mode,
            consent_alerts, alert_contact, alert_channel, preferred_checkin_time,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            name,
            course,
            year,
            campus,
            "English",
            1,
            0,
            "",
            "Mentor",
            "20:00",
            today,
            today,
        ),
    )


def _insert_log_series(user_id: str, base_records: list[tuple]) -> None:
    existing = fetch_one("SELECT COUNT(*) AS count FROM mood_logs WHERE user_id = ?", (user_id,))
    if existing and existing["count"] > 0:
        return

    today = date.today()
    for day_offset in range(14):
        template = base_records[day_offset % len(base_records)]
        mood_label, mood_score, stress, energy, sleep, attendance, assignments, social, exam, notes = (
            template
        )
        log_date = (today - timedelta(days=13 - day_offset)).isoformat()
        risk_score = min(
            100.0,
            (6 - mood_score) * 11
            + stress * 4
            + (10 - energy) * 3
            + max(0.0, 7 - sleep) * 6
            + assignments * 4
            + (6 - social) * 5
            + exam * 2,
        )
        if risk_score >= 72:
            risk_label = "High Risk"
        elif risk_score >= 42:
            risk_label = "Stressed"
        else:
            risk_label = "Normal"

        execute(
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
                user_id,
                log_date,
                mood_label,
                mood_score,
                stress,
                energy,
                sleep,
                attendance,
                assignments,
                social,
                exam,
                encrypt_text(notes),
                0.15 if mood_score >= 4 else -0.25 if mood_score <= 2 else 0.02,
                0.45,
                mood_label.lower(),
                risk_label,
                risk_score,
                log_date,
            ),
        )


def seed_peer_posts() -> None:
    existing = fetch_one("SELECT COUNT(*) AS count FROM peer_posts")
    if existing and existing["count"] > 0:
        return

    today = date.today().isoformat()
    for alias, topic, message in DEMO_POSTS:
        execute(
            """
            INSERT INTO peer_posts (alias, topic, message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (alias, topic, message, today),
        )


def seed_demo_user(user_id: str) -> None:
    _insert_profile(user_id, "Demo Student", "B.Tech CSE", 2, "Main Campus")
    base_records = [
        ("Focused", 4, 4, 7, 7.3, 92, 1, 4, 4, "Had a productive lab session and felt steady."),
        ("Tired", 3, 6, 4, 5.8, 87, 2, 3, 6, "Low sleep because of assignment deadlines."),
        ("Overwhelmed", 2, 8, 3, 4.9, 78, 4, 2, 8, "Too many deadlines together. Hard to focus."),
        ("Okay", 3, 5, 5, 6.4, 84, 2, 3, 5, "Average day. Better after talking to a friend."),
        ("Calm", 4, 3, 8, 7.6, 95, 1, 4, 3, "Morning walk helped me reset before class."),
        ("Anxious", 2, 8, 4, 5.2, 82, 3, 2, 9, "Upcoming exam is making me overthink everything."),
        ("Hopeful", 4, 4, 7, 7.0, 91, 1, 4, 4, "Finished an assignment and felt relieved."),
    ]
    _insert_log_series(user_id, base_records)


def seed_demo_cohort() -> None:
    cohort_patterns = {
        "cohort-ananya": [
            ("Motivated", 4, 4, 8, 7.4, 94, 1, 4, 4, "Feeling focused and back on track."),
            ("Tired", 3, 5, 5, 6.2, 88, 2, 3, 6, "Lab submissions made the week heavy."),
        ],
        "cohort-rohan": [
            ("Anxious", 2, 8, 4, 5.1, 76, 4, 2, 8, "Internal assessments are piling up."),
            ("Okay", 3, 6, 5, 6.0, 81, 3, 3, 7, "Managing, but still feeling behind."),
        ],
        "cohort-meera": [
            ("Calm", 4, 3, 7, 7.8, 93, 1, 4, 3, "Good support circle this week."),
            ("Hopeful", 4, 4, 7, 7.1, 91, 1, 5, 4, "Routine is helping my balance."),
        ],
        "cohort-arjun": [
            ("Overwhelmed", 2, 9, 3, 4.8, 70, 5, 2, 9, "Placement prep and project work are colliding."),
            ("Low", 2, 8, 4, 5.3, 74, 4, 2, 8, "Not feeling like myself this week."),
        ],
    }

    for user_id, name, course, year, campus in COHORT_PROFILES:
        _insert_profile(user_id, name, course, year, campus)
        _insert_log_series(user_id, cohort_patterns[user_id])
