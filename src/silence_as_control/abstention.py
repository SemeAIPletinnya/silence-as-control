"""Abstention helpers."""

SILENCE_TOKEN = {"status": "abstained", "reason": "control_abstention"}


def control_abstention():
    """Return a stable abstention payload."""
    return dict(SILENCE_TOKEN)
