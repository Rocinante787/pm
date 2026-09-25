# Database Architecture & Modeling

## Overview

The Project Management MVP uses a lightweight SQLite local database. The database is automatically initialized and seeded on application startup if it does not already exist.

## Storage Pattern: Single JSON Document per User

Each user has a single record in the `user_boards` table containing their complete Kanban board represented as a serialized JSON string.

### Rationale
1. **Direct AI Compatibility:** The sidebar AI assistant (`openai/gpt-oss-120b`) reads and generates the full board context directly as structured JSON.
2. **1:1 Alignment with Frontend:** Matches the frontend state model (`BoardData`), eliminating complex object-relational mapping and joins.
3. **Simplicity:** Strictly satisfies the project guideline: *NEVER over-engineer, ALWAYS simplify*.

## Schema Definition

```sql
CREATE TABLE IF NOT EXISTS user_boards (
    user_id TEXT PRIMARY KEY,
    board_data TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Column Specifications
- `user_id`: Unique identifier for the user account (e.g. `'user'`). Supports future multi-user scaling.
- `board_data`: Complete serialized JSON object containing columns and cards.
- `updated_at`: Timestamp recording the last board modification.

## JSON Data Structure

The `board_data` JSON payload conforms to the following schema:

```json
{
  "columns": [
    {
      "id": "col-backlog",
      "title": "Backlog",
      "cardIds": ["card-1", "card-2"]
    },
    {
      "id": "col-discovery",
      "title": "Discovery",
      "cardIds": ["card-3"]
    },
    {
      "id": "col-progress",
      "title": "In Progress",
      "cardIds": ["card-4", "card-5"]
    },
    {
      "id": "col-review",
      "title": "Review",
      "cardIds": ["card-6"]
    },
    {
      "id": "col-done",
      "title": "Done",
      "cardIds": ["card-7", "card-8"]
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Align roadmap themes",
      "details": "Draft quarterly themes with impact statements and metrics."
    }
  }
}
```

## Database Persistence & Location

- Default local path: `data/pm.db` relative to project root.
- In Docker container: `/app/data/pm.db`.
- Configurable via `DATABASE_PATH` environment variable.
- The parent directory `data/` is mounted as a volume in Docker (`-v ./data:/app/data`) so data persists across container restarts and image updates.

## Initialization & Seeding Lifecycle

On backend startup (`lifespan` handler):
1. Verifies if database file and directory exist; creates them if missing.
2. Executes `CREATE TABLE IF NOT EXISTS user_boards`.
3. Checks if a row for `user_id = 'user'` exists.
4. If missing, populates `user` with the default 5 columns and 8 cards.

