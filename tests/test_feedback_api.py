import pytest
from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)

def test_post_feedback_success():
    query_id = str(uuid.uuid4())
    feedback_payload = {
        "query_id": query_id,
        "rating": 1,
        "comment": "Very helpful!"
    }
    response = client.post("/feedback", json=feedback_payload)
    assert response.status_code == 200
    assert response.json()["query_id"] == query_id
    assert response.json()["rating"] == 1

def test_post_feedback_invalid_rating():
    feedback_payload = {
        "query_id": "test-id",
        "rating": 5, # Only 0 or 1 allowed
        "comment": "Invalid"
    }
    response = client.post("/feedback", json=feedback_payload)
    # This might be 400 or 422 depending on implementation
    assert response.status_code in [400, 422]
