import os
import httpx
from openai import OpenAI

XAI_BASE_URL = "https://api.x.ai/v1"
DEFAULT_MODEL = "grok-4"

def get_xai_client() -> OpenAI:
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise RuntimeError("XAI_API_KEY is not set")
    return OpenAI(
        api_key=api_key,
        base_url=XAI_BASE_URL,
        timeout=httpx.Timeout(3600.0),
    )

def generate_candidate(
    prompt: str,
    system_prompt: str = "You are a precise technical assistant.",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
) -> str:
    client = get_xai_client()
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    message = resp.choices[0].message
    content = message.content if message and message.content else ""
    return content.strip()