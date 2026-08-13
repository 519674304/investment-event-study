from fastapi.testclient import TestClient

from event_study.api.app import create_app


def test_health_reports_application_and_schema_versions() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "applicationVersion": "0.1.0",
        "schemaVersion": "0001",
    }
