from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fetch_board():
    response = client.get("/api/board")
    assert response.status_code == 200
    data = response.json()
    assert "columns" in data
    assert "cards" in data
    assert len(data["columns"]) == 5
    assert len(data["cards"]) >= 8

def test_update_board():
    # Fetch current board
    res = client.get("/api/board")
    board = res.json()

    # Add a new card
    card_id = "card-api-test-1"
    board["cards"][card_id] = {
        "id": card_id,
        "title": "API Created Card",
        "details": "Details from pytest",
    }
    board["columns"][0]["cardIds"].append(card_id)

    # Put update
    put_res = client.put("/api/board", json=board)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert card_id in updated["cards"]
    assert updated["cards"][card_id]["title"] == "API Created Card"

    # Verify subsequent GET returns the persisted card
    get_res = client.get("/api/board")
    assert card_id in get_res.json()["cards"]

def test_update_board_invalid_schema():
    # Missing required 'columns' key
    bad_payload = {"cards": {}}
    response = client.put("/api/board", json=bad_payload)
    assert response.status_code == 422

def test_reset_board():
    # Call reset
    response = client.post("/api/board/reset")
    assert response.status_code == 200
    data = response.json()
    assert len(data["columns"]) == 5
    assert len(data["cards"]) == 8
    # Confirm the temporary card added in test_update_board is gone
    assert "card-api-test-1" not in data["cards"]
