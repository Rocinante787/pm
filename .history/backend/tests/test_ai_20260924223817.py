import pytest
from httpx import AsyncClient
import os

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_openrouter_api_key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "dummy_key_for_testing")

async def test_ai_test_endpoint_no_key(async_client: AsyncClient, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    response = await async_client.post("/api/ai/test", json={"prompt": "hello"})
    assert response.status_code == 500

async def test_ai_chat_endpoint_schema(async_client: AsyncClient, mock_openrouter_api_key, mocker):
    # Mock the AsyncOpenAI client
    mock_client = mocker.AsyncMock()
    mock_choice = mocker.Mock()
    mock_choice.message.content = '{"message": "Hello", "board_update": null}'
    mock_client.chat.completions.create.return_value.choices = [mock_choice]
    
    mocker.patch("app.ai.get_ai_client", return_value=mock_client)
    
    board_payload = {
        "columns": [],
        "cards": {}
    }
    
    response = await async_client.post(
        "/api/ai/chat",
        json={"prompt": "Say hello", "board": board_payload}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello"
    assert data["board_update"] is None

async def test_ai_chat_endpoint_update_board(async_client: AsyncClient, mock_openrouter_api_key, mocker):
    # Mock the AsyncOpenAI client
    mock_client = mocker.AsyncMock()
    mock_choice = mocker.Mock()
    mock_choice.message.content = '''{
        "message": "Card added",
        "board_update": {
            "columns": [{"id": "col1", "title": "Todo", "cardIds": ["c1"]}],
            "cards": {"c1": {"id": "c1", "title": "New Card", "details": "Det"}}
        }
    }'''
    mock_client.chat.completions.create.return_value.choices = [mock_choice]
    
    mocker.patch("app.ai.get_ai_client", return_value=mock_client)
    mocker.patch("app.ai.save_board", new_callable=mocker.AsyncMock)
    
    board_payload = {
        "columns": [{"id": "col1", "title": "Todo", "cardIds": []}],
        "cards": {}
    }
    
    response = await async_client.post(
        "/api/ai/chat",
        json={"prompt": "Add a card", "board": board_payload}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Card added"
    assert data["board_update"] is not None
    assert data["board_update"]["cards"]["c1"]["title"] == "New Card"
