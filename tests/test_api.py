from __future__ import annotations


def test_health_and_dashboard_routes(isolated_env):
    from backend import create_app

    app = create_app()
    client = app.test_client()

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"

    dashboard = client.get("/api/dashboard/demo-student?days=14")
    assert dashboard.status_code == 200
    assert "metrics" in dashboard.get_json()

    provider_status = client.get("/api/alerts/provider-status")
    assert provider_status.status_code == 200
    assert "email" in provider_status.get_json()
