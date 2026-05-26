from fastapi.testclient import TestClient

from app.main import app


def test_health_and_auth():
    with TestClient(app) as client:
        assert client.get("/health").json()["ok"] is True
        response = client.post("/api/auth/login", json={"email": "admin@appsec.local", "password": "AppSecPilot123!"})
        assert response.status_code == 200
        token = response.json()["access_token"]
        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.json()["email"] == "admin@appsec.local"


def test_projects_seeded():
    with TestClient(app) as client:
        response = client.get("/api/projects")
        assert response.status_code == 200
        assert response.json()
