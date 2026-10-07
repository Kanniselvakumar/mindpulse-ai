from __future__ import annotations

from typing import Any


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def build_recommendations(
    checkin: Any,
    text_analysis: dict[str, Any],
    risk: dict[str, Any],
    streak: int = 0,
) -> dict[str, Any]:
    actions: list[str] = []
    study_hacks: list[str] = []
    habit_stack: list[str] = []

    if risk["label"] == "High Risk":
        actions.append("Pause for 10 minutes and speak with a trusted person or campus mentor today.")
        actions.append("Use the resource hub now and keep emergency contacts visible.")
    elif risk["label"] == "Stressed":
        actions.append("Break your workload into one 25-minute sprint and one 5-minute reset.")
    else:
        actions.append("Protect what is working by keeping your next self-care action small and consistent.")

    if checkin.stress_score >= 8:
        actions.append("Try a 4-4-6 breathing cycle for three rounds before your next task.")
        study_hacks.append("Make a 'must-do / should-do / can-wait' list to cut overload.")

    if checkin.sleep_hours < 6:
        actions.append("Plan an earlier shutdown tonight and avoid screens for the last 20 minutes.")
        habit_stack.append("Sleep reset: dim lights, water, phone away, then 5-minute stretch.")

    if checkin.assignments_due >= 3 or checkin.exam_pressure >= 8:
        study_hacks.append("Use exam triage: revise one high-weight topic before chasing everything.")
        habit_stack.append("Write the first tiny step for your hardest assignment right now.")

    if checkin.social_connectedness <= 2:
        actions.append("Message one friend, classmate, or family member instead of isolating today.")

    if text_analysis.get("emotion") in {"anxiety", "burnout"}:
        habit_stack.append("Brain dump every worry onto paper, then circle only one thing you can act on.")

    if checkin.energy_score <= 4:
        habit_stack.append("Take a sunlight + water break before starting the next study block.")

    if streak >= 7:
        badge = "Consistency Champion"
    elif streak >= 3:
        badge = "Momentum Builder"
    else:
        badge = "Fresh Start"

    if risk["label"] == "High Risk":
        daily_challenge = "Complete one check-in, one breathing reset, and one human conversation today."
    elif checkin.mood_score >= 4:
        daily_challenge = "Lock in the good day by repeating one habit that helped."
    else:
        daily_challenge = "Protect your energy with one low-pressure win in the next hour."

    return {
        "priority_actions": _unique(actions)[:4],
        "study_hacks": _unique(study_hacks)[:3],
        "habit_stack": _unique(habit_stack)[:4],
        "daily_challenge": daily_challenge,
        "badge": badge,
        "breathing_exercise": [
            "Inhale for 4 seconds",
            "Hold for 4 seconds",
            "Exhale for 6 seconds",
            "Repeat 3 times",
        ],
    }
