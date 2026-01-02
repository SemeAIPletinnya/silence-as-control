"""
LangChain Adapter
=================
Integrate silence-as-control into LangChain pipelines.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

# Import from silence layer
SILENCE: Optional[str] = None
COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3


def should_silence(coherence: float, drift: float) -> bool:
    return coherence < COHERENCE_THRESHOLD or drift > DRIFT_THRESHOLD


class SilenceGatedChain:
    """
    Wraps a LangChain chain with silence gating.

    Usage:
        chain = LLMChain(...)
        gated_chain = SilenceGatedChain(chain, coherence_fn, drift_fn)
        result = gated_chain.run(query)  # Returns None if gated
    """

    def __init__(
        self,
        chain: Any,
        coherence_fn: Callable[[str, str], float],
        drift_fn: Callable[[list[str], str], float],
    ) -> None:
        self.chain = chain
        self.coherence_fn = coherence_fn
        self.drift_fn = drift_fn
        self.history: list[str] = []

    def run(self, query: str) -> Optional[str]:
        """Execute chain with silence gate."""
        # Get response from underlying chain
        response = self.chain.run(query)

        # Measure state
        coherence = self.coherence_fn(query, response)
        drift = self.drift_fn(self.history, response)

        # Apply gate
        if should_silence(coherence, drift):
            return SILENCE

        # Update history
        self.history.append(response)
        return response

    def reset(self) -> None:
        """Clear history."""
        self.history = []


# =============================================================================
# CALLBACK INTEGRATION
# =============================================================================


class SilenceCallback:
    """
    LangChain callback for logging silence decisions.

    Usage:
        callback = SilenceCallback()
        chain.run(query, callbacks=[callback])
    """

    def __init__(self) -> None:
        self.silence_events: list[dict[str, object]] = []

    def on_silence(self, coherence: float, drift: float, query: str) -> None:
        self.silence_events.append(
            {
                "coherence": coherence,
                "drift": drift,
                "query": query,
            }
        )

    def get_events(self) -> list[dict[str, object]]:
        return self.silence_events
