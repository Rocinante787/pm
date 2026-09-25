from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    response = client.post("/api/auth/login", json={"username": "user", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user"
    assert data["token"] == "token-user-pm-session"

def test_login_failure():
    response = client.post("/api/auth/login", json={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

def test_get_current_user():
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer token-user-pm-session"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "user"

def test_get_current_user_unauthorized():
    response = client.get("/api/auth/me")
    assert response.status_code == 401

