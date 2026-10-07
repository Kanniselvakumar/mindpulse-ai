from __future__ import annotations


def test_submit_checkin_and_dashboard(isolated_env):
    import backend.app_platform as platform

    result = platform.submit_check_in(
        {
            "user_id": "demo-student",
            "name": "Demo Student",
            "course": "B.Tech CSE",
            "year": 2,
            "campus": "Main Campus",
            "language": "English",
            "anonymous_mode": False,
            "consent_alerts": True,
            "alert_contact": "Faculty Mentor",
            "alert_channel": "Mentor",
            "mood_label": "Overwhelmed",
            "mood_score": 2,
            "stress_score": 9,
            "energy_score": 3,
            "sleep_hours": 4.5,
            "attendance_rate": 72,
            "assignments_due": 4,
            "social_connectedness": 2,
            "exam_pressure": 9,
            "notes": "I feel overwhelmed and exhausted before exams.",
        }
    )

    assert result["risk"]["label"] in {"Stressed", "High Risk"}
    assert result["risk"]["selected_model"] in {"Logistic Regression", "Random Forest"}
    assert result["risk"]["dataset_source"] == "Simulated student wellness dataset"
    dashboard = platform.get_dashboard("demo-student", 30)
    assert dashboard["metrics"]["total_checkins"] >= 1
    assert dashboard["latest_entry"] is not None


def test_moderate_checkin_does_not_saturate_risk_score(isolated_env):
    import backend.app_platform as platform

    result = platform.submit_check_in(
        {
            "user_id": "demo-student",
            "name": "Demo Student",
            "course": "B.Tech CSE",
            "year": 2,
            "campus": "Main Campus",
            "language": "English",
            "anonymous_mode": False,
            "consent_alerts": False,
            "alert_contact": "Faculty Mentor",
            "alert_channel": "Mentor",
            "mood_label": "Focused",
            "mood_score": 4,
            "stress_score": 5,
            "energy_score": 6,
            "sleep_hours": 7.0,
            "attendance_rate": 88,
            "assignments_due": 1,
            "social_connectedness": 3,
            "exam_pressure": 5,
            "notes": "",
        }
    )

    assert result["risk"]["risk_score"] < 100.0
    assert result["risk"]["label"] in {"Normal", "Stressed"}


def test_ml_overview_exposes_dataset_and_models(isolated_env):
    import backend.app_platform as platform

    overview = platform.get_ml_overview()

    assert overview["selected_model"] in {"Logistic Regression", "Random Forest"}
    assert overview["dataset"]["source"] == "Simulated student wellness dataset"
    assert len(overview["models_tested"]) == 2


def test_peer_support_helpers(isolated_env):
    import backend.app_platform as platform

    post = platform.create_peer_post(
        {
            "alias": "Anonymous",
            "topic": "Daily Win",
            "message": "I made it through a hard day.",
        }
    )
    matches = platform.get_buddy_matches("demo-student")

    assert post["topic"] == "Daily Win"
    assert len(matches) >= 1
