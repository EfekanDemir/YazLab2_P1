import pytest
from fastapi.testclient import TestClient
import respx
import httpx
from unittest.mock import patch
from src.main import app, route_store

client = TestClient(app)

# Mock the redis get_route_config
def mock_get_route_config(path: str, method: str):
    min_role = "anonymous"
    if path.startswith("/api/v1/products"):
        return {"min_required_role": min_role, "target_service": "http://service-1-product:5002", "is_active": True, "_calculated_target_url": f"http://service-1-product:5002{path}"}
    if path.startswith("/api/v1/auth"):
        return {"min_required_role": min_role, "target_service": "http://auth-service:5001", "is_active": True, "_calculated_target_url": f"http://auth-service:5001{path}"}
    if path.startswith("/api/v1/timeout"):
        return {"min_required_role": min_role, "target_service": "http://service-1-product:5002", "is_active": True, "_calculated_target_url": f"http://service-1-product:5002{path}"}
    return None

patcher = patch.object(route_store, 'get_route_config', side_effect=mock_get_route_config)
patcher.start()

def test_dispatcher_health():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["service"] == "dispatcher"

# 1. & 2. & 3. Dinamik Rota, HTTP Metotları ve Body/Header Geçirgenliği
@respx.mock
def test_routing_to_product_service():
    # Mocking target service
    mock_route = respx.get("http://service-1-product:5002/api/v1/products").mock(
        return_value=httpx.Response(200, json={"items": ["product1", "product2"]})
    )
    
    # Request to Dispatcher
    response = client.get(
        "/api/v1/products", 
        headers={"Authorization": "Bearer fake_token"}
    )
    
    assert response.status_code == 200
    assert response.json() == {"items": ["product1", "product2"]}
    assert mock_route.called
    assert mock_route.calls[0].request.headers["Authorization"] == "Bearer fake_token"

@respx.mock
def test_routing_to_auth_service_with_body():
    mock_route = respx.post("http://auth-service:5001/api/v1/auth/login").mock(
        return_value=httpx.Response(201, json={"token": "jwt_token"})
    )
    
    payload = {"username": "admin", "password": "123"}
    response = client.post("/api/v1/auth/login", json=payload)
    
    assert response.status_code == 201
    assert response.json() == {"token": "jwt_token"}
    assert mock_route.called
    
    import json
    assert json.loads(mock_route.calls[0].request.content.decode('utf-8')) == payload

# 4. 404 Not Found (Rota Yok)
def test_404_not_found():
    response = client.get("/api/v1/unknown-route")
    assert response.status_code == 404
    
    data = response.json()
    assert "error" in data
    assert data["code"] == 404

# 5. 504 Gateway Error (Hedef Timeout/Kapalı)
@respx.mock
def test_504_gateway_timeout():
    # Simulate a timeout from the downstream service
    respx.get("http://service-1-product:5002/api/v1/products/timeout").mock(
        side_effect=httpx.ConnectTimeout("Mocked timeout")
    )
    
    response = client.get("/api/v1/products/timeout")
    assert response.status_code == 504
    
    data = response.json()
    assert "error" in data
    assert data["code"] == 504

# 6. 413 Payload Too Large
def test_413_payload_too_large():
    # Create 6MB string
    large_body = "x" * (6 * 1024 * 1024)
    response = client.post(
        "/api/v1/products", 
        data=large_body,
        headers={"Content-Type": "text/plain"}
    )
    assert response.status_code == 413
    
    data = response.json()
    assert "error" in data
    assert data["code"] == 413
