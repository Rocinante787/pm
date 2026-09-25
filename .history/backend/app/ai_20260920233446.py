import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
import httpx

# Load .env from backend or root directory
env_path_root = Path(__file__).resolve().parent.parent.parent / ".env"
env_path_backend = Path(__file__).resolve().parent.parent / ".env"
if env_path_root.exists():
    load_dotenv(env_path_root)
elif env_path_backend.exists():
    load_dotenv(env_path_backend)
else:
    load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-120b"
FREE_FALLBACK_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

router = APIRouter(prefix="/api/ai", tags=["ai"])

from pydantic import BaseModel

class AiCommandRequest(BaseModel):
    prompt: str
    board: dict

    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY is not configured in environment or .env file",
        )
    return key

async def call_openrouter(
    messages: list[dict[str, str]],
    model: str | None = None,
    response_format: dict | None = None,
    temperature: float = 0.2,
) -> tuple[str, str]:
    """
    Calls OpenRouter chat completions.
    Returns (assistant_content, model_used).
    """
    api_key = get_api_key()
    primary_model = model or os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)
    selected_model = primary_model

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Project Management MVP",
    }

    payload: dict = {
        "model": selected_model,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format:
        payload["response_format"] = response_format

    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            response = await client.post(
                OPENROUTER_BASE_URL,
                headers=headers,
                json=payload,
            )

            # If paid model has insufficient credits (402), gracefully fall back to free 120b model
            if response.status_code == 402 and selected_model != FREE_FALLBACK_MODEL:
                selected_model = FREE_FALLBACK_MODEL
                payload["model"] = selected_model
                response = await client.post(
                    OPENROUTER_BASE_URL,
                    headers=headers,
                    json=payload,
                )

            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise HTTPException(status_code=502, detail="No choices returned from OpenRouter")
            content = choices[0]["message"]["content"]
            return content.strip(), selected_model
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            detail = exc.response.text
            raise HTTPException(
                status_code=502,
                detail=f"OpenRouter API error (HTTP {status}): {detail}",
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=504,
                detail=f"Network error connecting to OpenRouter: {str(exc)}",
            )

    @router.post("/command")
    async def execute_ai_command(request: dict):
        """
        Accepts a user prompt, forwards to OpenRouter, expects a JSON list of actions
        to mutate the board. Applies actions via DB utilities and returns the
        updated board.
        """
        # Expected payload structure
        # { "prompt": "...", "board": { ... } }
        prompt = request.get("prompt")
        board_data = request.get("board")
        if not prompt or not isinstance(board_data, dict):
            raise HTTPException(status_code=400, detail="Invalid request payload")

        # Build messages for the model. Provide the current board JSON as context.
        system_msg = {
            "role": "system",
            "content": (
                "You are an assistant that can modify a Kanban board. "
                "Return ONLY a JSON array of actions. Each action must be an object with a "
                "'action' field (create, edit, move, delete) and the necessary parameters. "
                "Do NOT include any explanatory text."
            ),
        }
        user_msg = {"role": "user", "content": f"Prompt: {prompt}\nBoard: {board_data}"}
        messages = [system_msg, user_msg]

        # Call the model (fallback handled inside call_openrouter)
        result, used_model = await call_openrouter(messages=messages)
        # Expect result to be a JSON string
        try:
            import json as _json
            actions = _json.loads(result)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Model returned invalid JSON: {exc}")

        # Simple validation of actions format
        valid_actions = {"create", "edit", "move", "delete"}
        for act in actions:
            if not isinstance(act, dict) or act.get("action") not in valid_actions:
                raise HTTPException(status_code=400, detail="Invalid action format in model response")

        # Apply actions using DB helpers (import lazily to avoid circular imports)
        from .db import save_board, get_board
        user_id = "user"  # MVP single user
        # Load current board from DB to ensure consistency
        current_board = await get_board(user_id)
        # Apply each action sequentially (very simple implementation)
        for act in actions:
            a_type = act["action"]
            if a_type == "create":
                # Expect card fields: title, details, columnId
                card = {
                    "id": act.get("id") or "tmp-" + str(len(current_board.columns)),
                    "title": act.get("title", "Untitled"),
                    "details": act.get("details", ""),
                }
                # Find column
                col_id = act.get("columnId")
                for col in current_board.columns:
                    if col.id == col_id:
                        col.cards.append(card)  # type: ignore[arg-type]
                        break
            elif a_type == "edit":
                card_id = act.get("cardId")
                for col in current_board.columns:
                    for c in col.cards:
                        if c.id == card_id:
                            c.title = act.get("title", c.title)
                            c.details = act.get("details", c.details)
            elif a_type == "move":
                card_id = act.get("cardId")
                src = act.get("fromColumnId")
                dst = act.get("toColumnId")
                moving_card = None
                for col in current_board.columns:
                    if col.id == src:
                        for i, c in enumerate(col.cards):
                            if c.id == card_id:
                                moving_card = c
                                del col.cards[i]
                                break
                if moving_card:
                    for col in current_board.columns:
                        if col.id == dst:
                            col.cards.append(moving_card)  # type: ignore[arg-type]
                            break
            elif a_type == "delete":
                card_id = act.get("cardId")
                for col in current_board.columns:
                    col.cards = [c for c in col.cards if c.id != card_id]
        # Persist the mutated board
        await save_board(current_board, user_id)
        return {"board": current_board, "model": used_model}

