import pytest
from app.db import init_db, get_board, save_board, reset_board
from app.models import BoardData, Column, Card

@pytest.fixture
def test_db_path(tmp_path):
    db_file = tmp_path / "test_pm.db"
    return db_file

def test_init_db_creates_and_seeds(test_db_path):
    # Ensure fresh DB gets created and seeded with default data
    init_db(test_db_path)
    board = get_board("user", test_db_path)
    assert board is not None
    assert isinstance(board, BoardData)
    assert len(board.columns) == 5
    assert len(board.cards) == 8
    assert "col-backlog" in [c.id for c in board.columns]
    assert "card-1" in board.cards
    assert board.cards["card-1"].title == "Align roadmap themes"

def test_save_board_persists_changes(test_db_path):
    init_db(test_db_path)
    board = get_board("user", test_db_path)
    assert board is not None

    # Add a new card
    new_card = Card(id="card-test-99", title="Test Title", details="Test Details")
    board.cards["card-test-99"] = new_card
    board.columns[0].cardIds.append("card-test-99")

    saved = save_board(board, "user", test_db_path)
    assert "card-test-99" in saved.cards

    # Re-fetch from fresh connection
    fetched = get_board("user", test_db_path)
    assert fetched is not None
    assert "card-test-99" in fetched.cards
    assert fetched.cards["card-test-99"].title == "Test Title"
    assert "card-test-99" in fetched.columns[0].cardIds

def test_reset_board(test_db_path):
    init_db(test_db_path)
    board = get_board("user", test_db_path)
    assert board is not None

    # Clear all cards
    empty_board = BoardData(columns=[], cards={})
    save_board(empty_board, "user", test_db_path)
    assert len(get_board("user", test_db_path).columns) == 0

    # Reset back to initial
    reset = reset_board("user", test_db_path)
    assert len(reset.columns) == 5
    assert len(reset.cards) == 8
