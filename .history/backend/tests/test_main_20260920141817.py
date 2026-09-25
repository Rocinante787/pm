from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root_serves_kanban_board():
    response = client.get("/")
    assert response.status_code == 200
    assert "Kanban Studio" in response.text
    assert "text/html" in response.headers.get("content-type", "")
