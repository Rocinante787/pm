import os
import json
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI, APIStatusError
from app.models import BoardData
from app.db import save_board

# Load .env from backend or root directory
env_path_root = Path(__file__).resolve().parent.parent.parent / ".env"
env_path_backend = Path(__file__).resolve().parent.parent / ".env"
if env_path_root.exists():
    load_dotenv(env_path_root)
elif env_path_backend.exists():
    load_dotenv(env_path_backend)
else:
    load_dotenv()

router = APIRouter(prefix="/api/ai", tags=["ai"])

DEFAULT_MODEL = "openai/gpt-oss-120b"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def get_ai_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY is not configured in environment or .env file",
        )
    return AsyncOpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
    )

class AiTestRequest(BaseModel):
    prompt: str = "What is 2+2? Answer in one word."

class AiChatRequest(BaseModel):
    prompt: str
    board: BoardData

class AiChatResponse(BaseModel):
    message: str
    board_update: BoardData | None = None

@router.post("/test")
async def test_ai(request: AiTestRequest):
    client = get_ai_client()
    try:
        completion = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": request.prompt}],
        )
        return {"response": completion.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/chat", response_model=AiChatResponse)
async def chat_ai(request: AiChatRequest):
    client = get_ai_client()
    
    # We will use JSON mode to ask the AI to output exactly the JSON format we need
    system_prompt = (
        "You are an assistant for a Kanban board. You can answer questions about the board, "
        "and modify the board (create, edit, move cards). "
        "The board has columns and cards. Each card has an id, title, and details. "
        "You must respond with valid JSON matching this schema: "
        "{ \"message\": \"your reply to the user\", "
        "  \"board_update\": { \"columns\": [ ... ], \"cards\": { \"id\": { ... } } } } "
        "If you don't need to change the board, return null for board_update."
    )
    
    user_prompt = f"Prompt: {request.prompt}\nCurrent Board state (JSON): {request.board.model_dump_json()}"
    
    try:
        completion = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        
        response_text = completion.choices[0].message.content
        if not response_text:
             raise HTTPException(status_code=500, detail="Empty response from AI")
             
        data = json.loads(response_text)
        
        message = data.get("message", "")
        board_update = data.get("board_update")
        
        parsed_board = None
        if board_update:
            parsed_board = BoardData(**board_update)
            # save the new board state
            user_id = "user"
            await save_board(parsed_board, user_id)
            
        return AiChatResponse(message=message, board_update=parsed_board)
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"Model returned invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
