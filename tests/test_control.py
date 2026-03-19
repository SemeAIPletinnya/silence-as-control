from silence_as_control.control import por_control


def test_abstains_on_high_drift():
    assert por_control("hello", coherence=0.9, drift=0.31) == {
        "status": "abstained",
        "reason": "control_abstention",
    }


def test_abstains_on_low_coherence():
    assert por_control("hello", coherence=0.69, drift=0.1) == {
        "status": "abstained",
        "reason": "control_abstention",
    }


def test_allows_stable_output():
    assert por_control("hello", coherence=0.82, drift=0.15) == {
        "status": "ok",
        "output": "hello",
    }


def test_boundary_conditions_allow_output():
    assert por_control("edge", coherence=0.7, drift=0.3) == {
        "status": "ok",
        "output": "edge",
    }
