import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app import app

app.testing = True


def get_client():
    return app.test_client()


def test_health_check():
    client = get_client()
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "SMS Spam Detector API is running"


def test_predict_missing_message_key():
    client = get_client()
    response = client.post('/predict', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_predict_empty_message():
    client = get_client()
    response = client.post('/predict', json={"message": "   "})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_predict_valid_spam_message():
    client = get_client()
    response = client.post('/predict', json={
        "message": "WINNER!! You have been selected to receive a FREE prize. Call now to claim!"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "prediction" in data
    assert "probability" in data
    assert "safety_score" in data
    assert "confidence_label" in data
    assert data["prediction"] in [0, 1]
    assert 0 <= data["probability"] <= 1
    assert 0 <= data["safety_score"] <= 100


def test_predict_valid_ham_message():
    client = get_client()
    response = client.post('/predict', json={
        "message": "Hey, are we still meeting for lunch tomorrow at 1pm?"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "prediction" in data
    assert "probability" in data
    assert "safety_score" in data
    assert "confidence_label" in data


def test_predict_response_structure():
    client = get_client()
    response = client.post('/predict', json={"message": "Test message"})
    data = response.get_json()
    expected_keys = {"prediction", "probability", "safety_score", "confidence_label"}
    assert expected_keys.issubset(data.keys())


if __name__ == "__main__":
    import subprocess
    subprocess.run(["pytest", __file__, "-v"])