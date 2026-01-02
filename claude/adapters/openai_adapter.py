"""
OpenAI Adapter
==============
Integrate silence-as-control with OpenAI API calls.
"""

from typing import Callable

SILENCE = None
COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3


def should_silence(coherence: float, drift: float) -> bool:
    return coherence < COHERENCE_THRESHOLD or drift > DRIFT_THRESHOLD


def gated_completion(
    client,
    messages: list,
    model: str = "gpt-4",
    coherence_fn: Callable[[list, str], float] | None = None,
    drift_fn: Callable[[list, str], float] | None = None,
    **kwargs,
) -> str | None:
    """
    OpenAI completion with silence gate.

    Usage:
        from openai import OpenAI
        client = OpenAI()

        result = gated_completion(
            client,
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-4",
            coherence_fn=my_coherence_fn,
            drift_fn=my_drift_fn,
        )

        if result is None:
            print("[SILENCE]")
        else:
            print(result)
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )

    content = response.choices[0].message.content

    if coherence_fn and drift_fn:
        coherence = coherence_fn(messages, content)
        drift = drift_fn(messages, content)

        if should_silence(coherence, drift):
            return SILENCE

    return content


class GatedOpenAI:
    """
    Wrapper class for OpenAI client with built-in silence gating.

    Usage:
        gated = GatedOpenAI(client, coherence_fn, drift_fn)
        result = gated.chat("What is 2+2?")
    """

    def __init__(
        self,
        client,
        coherence_fn: Callable[[list, str], float],
        drift_fn: Callable[[list, str], float],
        model: str = "gpt-4",
    ):
        self.client = client
        self.coherence_fn = coherence_fn
        self.drift_fn = drift_fn
        self.model = model
        self.history: list = []

    def chat(self, query: str) -> str | None:
        """Send message with silence gating."""
        self.history.append({"role": "user", "content": query})

        result = gated_completion(
            self.client,
            messages=self.history,
            model=self.model,
            coherence_fn=self.coherence_fn,
            drift_fn=self.drift_fn,
        )

        if result is not None:
            self.history.append({"role": "assistant", "content": result})

        return result

    def reset(self):
        """Clear conversation history."""
        self.history = []
