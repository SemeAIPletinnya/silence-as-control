from __future__ import annotations

import os
from dataclasses import dataclass


class ModelAdapterError(RuntimeError):
    """Raised when a model adapter cannot answer."""


class ModelAdapter:
    """Interface for model responses used by the benchmark."""

    def answer(
        self,
        question: str,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> str:
        raise NotImplementedError

    def self_check(self, question: str, proposed_answer: str) -> str:
        raise NotImplementedError


@dataclass
class OpenAIChatAdapter(ModelAdapter):
    """OpenAI-compatible chat adapter.

    Uses deterministic settings by default (`temperature=0`).
    """

    model: str
    api_key_env: str = "OPENAI_API_KEY"
    base_url_env: str = "OPENAI_BASE_URL"
    timeout: float = 60.0

    def __post_init__(self) -> None:
        try:
            from openai import OpenAI
        except Exception as exc:  # noqa: BLE001
            raise ModelAdapterError(
                "openai package is required for provider='openai'. Install dependencies first."
            ) from exc

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise ModelAdapterError(
                f"Environment variable {self.api_key_env} is required for provider='openai'."
            )

        kwargs = {"api_key": api_key, "timeout": self.timeout}
        base_url = os.getenv(self.base_url_env)
        if base_url:
            kwargs["base_url"] = base_url

        self._client = OpenAI(**kwargs)

    def answer(
        self,
        question: str,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> str:
        try:
            request_kwargs = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Answer briefly and directly. If uncertain, provide your best factual answer.",
                    },
                    {"role": "user", "content": question},
                ],
                "temperature": temperature,
            }
            if seed is not None:
                request_kwargs["seed"] = seed

            resp = self._client.chat.completions.create(
                **request_kwargs,
            )
            text = (resp.choices[0].message.content or "").strip()
            return text
        except Exception as exc:  # noqa: BLE001
            raise ModelAdapterError(f"Model call failed: {exc}") from exc

    def self_check(self, question: str, proposed_answer: str) -> str:
        prompt = (
            f"Question: {question}\n"
            f"Proposed answer: {proposed_answer}\n\n"
            "Is the proposed answer factually correct?\n"
            "Reply with exactly one token:\n"
            "YES\nNO\nUNSURE"
        )
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strict factual verifier."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            text = (resp.choices[0].message.content or "").strip().upper()
            if text.startswith("YES"):
                return "YES"
            if text.startswith("NO"):
                return "NO"
            return "UNSURE"
        except Exception as exc:  # noqa: BLE001
            raise ModelAdapterError(f"Model self-check failed: {exc}") from exc


def build_model_adapter(provider: str, model: str) -> ModelAdapter:
    provider_normalized = provider.strip().lower()
    if provider_normalized == "openai":
        return OpenAIChatAdapter(model=model)
    raise ModelAdapterError(
        f"Unsupported provider '{provider}'. Supported providers: openai."
    )
