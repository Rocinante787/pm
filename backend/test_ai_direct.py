import asyncio
import os
import traceback
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pathlib import Path

env_path_root = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path_root)
api_key = os.getenv("OPENROUTER_API_KEY")

async def main():
    if not api_key:
        print("API KEY NOT FOUND!")
        return
        
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    try:
        completion = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": "hello"}],
            response_format={ "type": "json_object" },
        )
        print("Success:", completion)
    except Exception as e:
        print("Exception:", str(e))
        traceback.print_exc()

asyncio.run(main())
