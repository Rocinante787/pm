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

def get_api_key() -> str:
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

@router.post("/test")
async def test_ai_connectivity():
    prompt = "What is 2+2? Answer with just the number 4."
    messages = [
        {"role": "user", "content": prompt},
    ]
    result, used_model = await call_openrouter(messages=messages)
    return {
        "prompt": prompt,
        "result": result,
        "model": used_model,
        "status": "ok",
    }
