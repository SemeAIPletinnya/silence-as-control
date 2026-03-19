from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_generate_ok_response():
    response = client.post(
        "/generate",
        json={"output": "text", "coherence": 0.82, "drift": 0.15},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "output": "text"}


def test_generate_abstained_response():
    response = client.post(
        "/generate",
        json={"output": "text", "coherence": 0.6, "drift": 0.1},
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "abstained",
        "reason": "control_abstention",
    }
