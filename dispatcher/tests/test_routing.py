import pytest
from src.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_dispatcher_health():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["service"] == "dispatcher"
    assert response.json()["status"] == "I am alive"

# İleride TDD döngüsünde Routing mantığı eklenecek
def test_dispatcher_routing_to_auth():
    pass
