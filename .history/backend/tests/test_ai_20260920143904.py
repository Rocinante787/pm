import os
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ai_test_endpoint_mocked():
    with patch("app.ai.call_openrouter", return_value="4"):
        response = client.post("/api/ai/test")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "4"
        assert data["status"] == "ok"
        assert "openai/gpt-oss-120b" in data["model"]

@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY is not set in environment"
)
def test_ai_test_live_connectivity():
    # Live test directly connecting to OpenRouter
    response = client.post("/api/ai/test")
    assert response.status_code == 200
    data = response.json()
    assert "4" in data["result"]
