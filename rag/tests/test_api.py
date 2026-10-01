from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_api_validation():
    response = client.post("/retrieve", json={"query": "x", "top_k": 999})
    assert response.status_code == 422
