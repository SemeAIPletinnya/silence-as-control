from silence_as_control.core import Decision, Signals, Thresholds, decide


def test_respond_when_all_signals_ok():
    signals = Signals(
        coherence=0.9,
        drift=0.1,
        conflict=0.0,
        ambiguity=0.0,
        continuity=True,
    )
    decision, meta = decide(signals, Thresholds())

    assert decision == Decision.RESPOND
    assert meta == {"reasons": []}


def test_silence_on_low_coherence():
    signals = Signals(
        coherence=0.5,
        drift=0.1,
        conflict=0.0,
        ambiguity=0.0,
        continuity=True,
    )
    decision, meta = decide(signals, Thresholds())

    assert decision == Decision.SILENCE
    assert ("A1", "low_coherence") in meta["reasons"]


def test_minimal_on_ambiguity_only():
    signals = Signals(
        coherence=0.9,
        drift=0.1,
        conflict=0.0,
        ambiguity=0.5,
        continuity=True,
    )
    decision, meta = decide(signals, Thresholds())

    assert decision == Decision.MINIMAL
    assert meta["reasons"] == [("A2", "ambiguity_detected")]


def test_silence_on_multiple_issues():
    signals = Signals(
        coherence=0.5,
        drift=0.4,
        conflict=0.3,
        ambiguity=0.0,
        continuity=False,
    )
    decision, meta = decide(signals, Thresholds())

    assert decision == Decision.SILENCE
    assert ("A1", "low_coherence") in meta["reasons"]
    assert ("D1", "context_drift") in meta["reasons"]
    assert ("C2", "inter_model_conflict") in meta["reasons"]
    assert ("K3", "continuity_invalid") in meta["reasons"]
