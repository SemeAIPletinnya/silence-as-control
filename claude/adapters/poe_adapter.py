"""
Poe Adapter
===========
Integrate silence-as-control with Poe Python bots.
"""

SILENCE = None
COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3


def should_silence(coherence: float, drift: float) -> bool:
    return coherence < COHERENCE_THRESHOLD or drift > DRIFT_THRESHOLD


def gated_bot_call(
    bot_name: str,
    prompt: str,
    coherence_fn=None,
    drift_fn=None,
    context: list = None,
    output=None,
):
    """
    Poe bot call with silence gate.

    Usage:
        result = gated_bot_call(
            "GPT-4o",
            "Explain quantum computing",
            coherence_fn=my_coherence_fn,
            drift_fn=my_drift_fn,
        )

        if result is None:
            # Silence triggered
            pass
        else:
            print(result.text)
    """
    import poe

    # Make the call
    response = poe.call(bot_name, prompt)

    # Apply gate if functions provided
    if coherence_fn and drift_fn:
        ctx = context or []
        coherence = coherence_fn(ctx, response.text)
        drift = drift_fn(ctx, response.text)

        if should_silence(coherence, drift):
            return SILENCE

    # Output if requested
    if output is not None:
        output.add_message(response.last)

    return response


class GatedPoeBot:
    """
    Wrapper for Poe bot with silence gating.

    Usage:
        gated = GatedPoeBot("Claude-3.5-Sonnet", coherence_fn, drift_fn)
        result = gated.call("What is 2+2?")
    """

    def __init__(
        self,
        bot_name: str,
        coherence_fn,
        drift_fn,
    ):
        self.bot_name = bot_name
        self.coherence_fn = coherence_fn
        self.drift_fn = drift_fn
        self.history: list = []

    def call(self, prompt: str, output=None):
        """Call bot with silence gating."""
        result = gated_bot_call(
            self.bot_name,
            prompt,
            coherence_fn=self.coherence_fn,
            drift_fn=self.drift_fn,
            context=self.history,
            output=output,
        )

        if result is not None and result is not SILENCE:
            self.history.append(result.text)

        return result

    def reset(self):
        """Clear history."""
        self.history = []
