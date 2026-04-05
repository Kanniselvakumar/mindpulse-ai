from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd

from backend.services.risk_engine import risk_engine


def _empty_dashboard() -> dict[str, Any]:
    return {
        "metrics": {
            "average_mood": 0.0,
            "average_stress": 0.0,
            "average_sleep": 0.0,
            "check_in_streak": 0,
            "high_risk_days": 0,
            "total_checkins": 0,
        },
        "timeline": [],
        "risk_distribution": [],
        "insights": [],
        "forecast": [],
        "badges": [],
        "latest_entry": None,
    }


def calculate_streak(log_dates: list[date]) -> int:
    if not log_dates:
        return 0

    unique_dates = sorted(set(log_dates), reverse=True)
    streak = 0
    expected = unique_dates[0]
    for current in unique_dates:
        if current == expected:
            streak += 1
            expected = expected - timedelta(days=1)
        elif current < expected:
            break
    return streak


def build_insights(frame: pd.DataFrame) -> list[str]:
    insights: list[str] = []
    if frame.empty:
        return insights

    if frame["sleep_hours"].mean() < 6.2 and frame["mood_score"].mean() < 3.2:
        insights.append("Lower sleep is tracking with lower mood in this time window.")
    if frame["exam_pressure"].mean() >= 7:
        insights.append("Exam pressure is a major stress driver right now.")
    if frame["attendance_rate"].mean() < 82 and frame["stress_score"].mean() >= 6:
        insights.append("Attendance dips and stress spikes are appearing together.")
    if (frame["social_connectedness"] <= 2).sum() >= 3:
        insights.append("There are repeated signs of isolation. Peer or mentor support may help.")
    if not insights:
        insights.append("Your mood pattern is fairly stable right now. Keep the healthy routines consistent.")
    return insights


def build_badges(frame: pd.DataFrame, streak: int) -> list[str]:
    badges: list[str] = []
    if streak >= 7:
        badges.append("7-Day Check-in Streak")
    if not frame.empty and frame["sleep_hours"].mean() >= 7:
        badges.append("Sleep Guardian")
    if not frame.empty and frame["mood_score"].tail(5).mean() >= frame["mood_score"].head(5).mean():
        badges.append("Bounce Back Badge")
    return badges


def build_dashboard(frame: pd.DataFrame) -> dict[str, Any]:
    if frame.empty:
        return _empty_dashboard()

    prepared = frame.copy()
    prepared["log_date"] = pd.to_datetime(prepared["log_date"])
    prepared = prepared.sort_values("log_date")
    streak = calculate_streak(prepared["log_date"].dt.date.tolist())

    metrics = {
        "average_mood": round(float(prepared["mood_score"].mean()), 2),
        "average_stress": round(float(prepared["stress_score"].mean()), 2),
        "average_sleep": round(float(prepared["sleep_hours"].mean()), 2),
        "check_in_streak": streak,
        "high_risk_days": int((prepared["risk_level"] == "High Risk").sum()),
        "total_checkins": int(len(prepared)),
    }

    timeline_columns = [
        "log_date",
        "mood_label",
        "mood_score",
        "stress_score",
        "sleep_hours",
        "attendance_rate",
        "assignments_due",
        "social_connectedness",
        "exam_pressure",
        "risk_level",
        "risk_score",
    ]
    timeline = prepared[timeline_columns].copy()
    timeline["log_date"] = timeline["log_date"].dt.date.astype(str)

    risk_distribution = (
        prepared["risk_level"]
        .value_counts()
        .rename_axis("risk_level")
        .reset_index(name="count")
        .to_dict(orient="records")
    )

    forecast_frame = prepared[["log_date", "mood_score", "stress_score"]].copy()
    forecast_frame["log_date"] = forecast_frame["log_date"].dt.date.astype(str)

    latest = prepared.iloc[-1].to_dict()
    latest["log_date"] = prepared.iloc[-1]["log_date"].date().isoformat()

    return {
        "metrics": metrics,
        "timeline": timeline.to_dict(orient="records"),
        "risk_distribution": risk_distribution,
        "insights": build_insights(prepared),
        "forecast": risk_engine.forecast_low_days(forecast_frame),
        "badges": build_badges(prepared, streak),
        "latest_entry": latest,
    }
