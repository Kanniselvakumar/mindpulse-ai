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


def test_support_reply_includes_question_words_and_is_unique():
    from backend.services.assistant import build_support_reply

    q1 = "I am struggling with organic chemistry lab assignments."
    q2 = "I feel lonely during weekend study sessions."

    resp1 = build_support_reply(q1, None, "English")
    resp2 = build_support_reply(q2, None, "English")

    assert resp1["reply"] != resp2["reply"]
    assert "organic" in resp1["reply"].lower() or "chemistry" in resp1["reply"].lower()
    assert "lonely" in resp2["reply"].lower() or "weekend" in resp2["reply"].lower()


def test_support_reply_languages():
    from backend.services.assistant import build_support_reply

    languages = ["English", "Tamil", "Hindi", "Telugu", "Kannada", "Kanada"]
    for lang in languages:
        resp = build_support_reply("How to handle exam pressure?", None, lang)
        assert resp["reply"] is not None
        assert len(resp["reply"]) > 0
