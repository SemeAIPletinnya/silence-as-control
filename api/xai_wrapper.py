import os
import logging
from openai import OpenAI

XAI_BASE_URL = "https://api.x.ai/v1"
FALLBACK_MODEL = "grok-4"
DEFAULT_MODEL = FALLBACK_MODEL
LOGGER = logging.getLogger(__name__)

def get_default_model() -> str:
    return os.getenv("XAI_MODEL") or FALLBACK_MODEL

def get_client() -> OpenAI:
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise RuntimeError("XAI_API_KEY is not set")
    return OpenAI(
        api_key=api_key,
        base_url=XAI_BASE_URL,
    )

def generate_candidate(
    prompt: str,
    system_prompt: str = "You are a precise technical assistant.",
    model: str | None = None,
    temperature: float = 0.0,
    timeout: float = 30.0,
) -> str:
    try:
        model = model or get_default_model()
        client = get_client()
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            timeout=timeout,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        content = resp.choices[0].message.content or ""
        return content.strip()
    except Exception as exc:
        LOGGER.exception("xai_generate_candidate_failed")
        raise RuntimeError("xai_generation_failed") from exc
