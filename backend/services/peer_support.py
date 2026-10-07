from __future__ import annotations

from typing import Any


BUDDY_PROFILES = [
    {
        "alias": "Study Sprint Sam",
        "course": "B.Tech CSE",
        "year": 2,
        "strength": "Pomodoro accountability",
        "availability": "Evenings",
    },
    {
        "alias": "Quiet Focus Riya",
        "course": "B.Tech IT",
        "year": 3,
        "strength": "Revision planning",
        "availability": "Morning library sessions",
    },
    {
        "alias": "Calm Notes Arjun",
        "course": "B.Tech CSE",
        "year": 2,
        "strength": "Exam stress grounding",
        "availability": "Weekend check-ins",
    },
    {
        "alias": "Team-Up Meena",
        "course": "B.Sc Psychology",
        "year": 3,
        "strength": "Reflective journaling",
        "availability": "After class",
    },
]


def suggest_buddies(profile: dict[str, Any]) -> list[dict[str, Any]]:
    course = profile.get("course", "")
    year = int(profile.get("year", 2))
    matches: list[tuple[int, dict[str, Any]]] = []
    for buddy in BUDDY_PROFILES:
        score = 0
        if buddy["course"] == course:
            score += 2
        if buddy["year"] == year:
            score += 2
        if abs(buddy["year"] - year) == 1:
            score += 1
        matches.append((score, buddy))

    ordered = sorted(matches, key=lambda item: item[0], reverse=True)
    results: list[dict[str, Any]] = []
    for score, buddy in ordered[:3]:
        results.append(
            {
                **buddy,
                "match_score": score,
                "reason": f"Shared academic context with support style: {buddy['strength']}.",
            }
        )
    return results
