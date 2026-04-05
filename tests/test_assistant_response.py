from __future__ import annotations


def test_support_reply_is_contextual():
    from backend.services.assistant import build_support_reply

    response = build_support_reply(
        "I am anxious about exams and I cannot focus at all.",
        {
            "risk_level": "Stressed",
            "exam_pressure": 9,
            "sleep_hours": 5.2,
            "stress_score": 8,
            "attendance_rate": 82,
        },
        "English",
    )

    assert response["focus_area"] in {"Exam Stress", "Anxiety"}
    assert len(response["support_plan"]) == 3
    assert "exam" in response["reply"].lower() or "focus" in response["reply"].lower()
