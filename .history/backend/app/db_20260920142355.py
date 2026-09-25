import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from app.models import BoardData

INITIAL_BOARD_DATA: dict[str, Any] = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
        {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
        {
            "id": "col-progress",
            "title": "In Progress",
            "cardIds": ["card-4", "card-5"],
        },
        {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
        {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
    ],
    "cards": {
        "card-1": {
            "id": "card-1",
            "title": "Align roadmap themes",
            "details": "Draft quarterly themes with impact statements and metrics.",
        },
        "card-2": {
            "id": "card-2",
            "title": "Gather customer signals",
            "details": "Review support tags, sales notes, and churn feedback.",
        },
        "card-3": {
            "id": "card-3",
            "title": "Prototype analytics view",
            "details": "Sketch initial dashboard layout and key drill-downs.",
        },
        "card-4": {
            "id": "card-4",
            "title": "Refine status language",
            "details": "Standardize column labels and tone across the board.",
        },
        "card-5": {
            "id": "card-5",
            "title": "Design card layout",
            "details": "Add hierarchy and spacing for scanning dense lists.",
        },
        "card-6": {
            "id": "card-6",
            "title": "QA micro-interactions",
            "details": "Verify hover, focus, and loading states.",
        },
        "card-7": {
            "id": "card-7",
            "title": "Ship marketing page",
            "details": "Final copy approved and asset pack delivered.",
        },
        "card-8": {
            "id": "card-8",
            "title": "Close onboarding sprint",
            "details": "Document release notes and share internally.",
        },
    },
}

def get_database_path() -> Path:
    custom_path = os.getenv("DATABASE_PATH")
    if custom_path:
        return Path(custom_path)
    # Default to data/pm.db in project root or app root
    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "pm.db"

def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    target_path = db_path or get_database_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path | None = None) -> None:
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_boards (
                user_id TEXT PRIMARY KEY,
                board_data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cursor = conn.execute(
            "SELECT 1 FROM user_boards WHERE user_id = ?",
            ("user",)
        )
        if not cursor.fetchone():
            conn.execute(
                """
                INSERT INTO user_boards (user_id, board_data)
                VALUES (?, ?)
                """,
                ("user", json.dumps(INITIAL_BOARD_DATA))
            )

def get_board(user_id: str = "user", db_path: Path | None = None) -> BoardData | None:
    conn = get_connection(db_path)
    with conn:
        cursor = conn.execute(
            "SELECT board_data FROM user_boards WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        raw_json = row["board_data"]
        data = json.loads(raw_json)
        return BoardData.model_validate(data)

def save_board(board: BoardData, user_id: str = "user", db_path: Path | None = None) -> BoardData:
    conn = get_connection(db_path)
    serialized = board.model_dump_json()
    with conn:
        conn.execute(
            """
            INSERT INTO user_boards (user_id, board_data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                board_data = excluded.board_data,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (user_id, serialized)
        )
    return board

def reset_board(user_id: str = "user", db_path: Path | None = None) -> BoardData:
    initial_model = BoardData.model_validate(INITIAL_BOARD_DATA)
    return save_board(initial_model, user_id, db_path)

