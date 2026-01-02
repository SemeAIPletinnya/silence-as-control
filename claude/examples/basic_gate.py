"""
Basic Gate Example
==================
Minimal example of silence-as-control.
"""

# =============================================================================
# THE PRIMITIVE
# =============================================================================

SILENCE = None
COHERENCE_THRESHOLD = 0.7
DRIFT_THRESHOLD = 0.3


def should_silence(coherence: float, drift: float) -> bool:
    """The entire primitive in one function."""
    return coherence < COHERENCE_THRESHOLD or drift > DRIFT_THRESHOLD


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example():
    # Scenario 1: High coherence, low drift → respond
    coherence, drift = 0.85, 0.1
    if should_silence(coherence, drift):
        print("Scenario 1: [SILENCE]")
    else:
        print("Scenario 1: Response allowed")

    # Scenario 2: Low coherence → silence
    coherence, drift = 0.5, 0.1
    if should_silence(coherence, drift):
        print("Scenario 2: [SILENCE] — low coherence")
    else:
        print("Scenario 2: Response allowed")

    # Scenario 3: High drift → silence
    coherence, drift = 0.9, 0.5
    if should_silence(coherence, drift):
        print("Scenario 3: [SILENCE] — high drift")
    else:
        print("Scenario 3: Response allowed")


if __name__ == "__main__":
    example()
