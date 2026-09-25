from fastapi import APIRouter, Header, HTTPException
from app.db import get_board, init_db, reset_board, save_board
from app.models import BoardData

router = APIRouter(prefix="/api/board", tags=["board"])

def get_authenticated_user_id(authorization: str | None = Header(default=None)) -> str:
    # For MVP with hardcoded user, accept token or default to "user"
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        if token == "token-user-pm-session":
            return "user"
    # Default to "user" for ease of MVP access
    return "user"

@router.get("", response_model=BoardData)
async def fetch_board(authorization: str | None = Header(default=None)):
    user_id = get_authenticated_user_id(authorization)
    board = get_board(user_id)
    if not board:
        init_db()
        board = get_board(user_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.put("", response_model=BoardData)
async def update_board(board: BoardData, authorization: str | None = Header(default=None)):
    user_id = get_authenticated_user_id(authorization)
    return save_board(board, user_id=user_id)

@router.post("/reset", response_model=BoardData)
async def reset_board_endpoint(authorization: str | None = Header(default=None)):
    user_id = get_authenticated_user_id(authorization)
    return reset_board(user_id=user_id)
