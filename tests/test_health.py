import os

from fastapi.testclient import TestClient

os.environ.setdefault("MOCK_MODE", "true")

from backend.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "mock_mode" in payload
