from __future__ import annotations


def test_register_and_login_user(isolated_env):
    import backend.app_platform as platform

    created = platform.register_user(
        {
            "name": "New Student",
            "email": "new.student@example.com",
            "phone_number": "+15551234567",
            "password": "Password@123",
            "confirm_password": "Password@123",
            "course": "B.Tech CSE",
            "year": 3,
            "campus": "Main Campus",
            "language": "English",
        }
    )
    logged_in = platform.login_user(
        {
            "email": "new.student@example.com",
            "password": "Password@123",
        }
    )

    assert created["email"] == "new.student@example.com"
    assert logged_in["profile"]["name"] == "New Student"
    assert logged_in["role"] == "student"


def test_provider_status_defaults_to_safe_mode(isolated_env):
    import backend.app_platform as platform

    status = platform.get_alert_provider_status()

    assert status["real_delivery_enabled"] is False
    assert status["email"]["configured"] is False
    assert status["sms"]["configured"] is False
