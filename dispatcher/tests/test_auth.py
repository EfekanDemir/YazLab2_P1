import pytest
from fastapi.testclient import TestClient
import jwt
import httpx
import respx
from datetime import datetime, timedelta

from src.main import app

client = TestClient(app)
SECRET_KEY = "test_secret_for_jwt"

# Helper for minting test tokens
def create_token(user_id: str, role: str, expires_in_minutes: int = 60):
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# 1. Test 401 Unauthorized (No Token)
def test_401_no_token():
    # Calling a protected route without Bearer token
    response = client.get("/api/v1/products")
    assert response.status_code == 401
    assert "error" in response.json()

# 2. Test 401 Unauthorized (Invalid / Expired Token)
def test_401_invalid_token():
    # Expired token
    expired_token = create_token("user1", "admin", -10)
    response = client.get(
        "/api/v1/products", 
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    
    # Garbage token
    response2 = client.get(
        "/api/v1/products", 
        headers={"Authorization": "Bearer garbage123"}
    )
    assert response2.status_code == 401

# 3. Test 403 Forbidden (Insufficient Role)
@respx.mock
def test_403_insufficient_role():
    # Mock route to ensure proxy isn't called
    mock_route = respx.delete("http://service-1-product:5002/api/v1/products/1").mock(
        return_value=httpx.Response(204)
    )
    
    customer_token = create_token("user_cust", "customer")
    # Assuming DELETE /api/v1/products requires 'admin' (This will be configured in our mock/redis)
    response = client.delete(
        "/api/v1/products/1",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    
    assert response.status_code == 403
    assert "error" in response.json()
    assert not mock_route.called

# 4. Test Success and Enrichment (Role: admin -> DELETE)
@respx.mock
def test_success_and_header_enrichment():
    # Mock target
    mock_route = respx.delete("http://service-1-product:5002/api/v1/products/1").mock(
        return_value=httpx.Response(204)
    )
    
    admin_token = create_token("user_admin", "admin")
    
    response = client.delete(
        "/api/v1/products/1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # 204 No Content expected per RMM rules for DELETE
    assert response.status_code == 204
    assert mock_route.called
    
    # Check Enrichment Headers
    passed_request = mock_route.calls[0].request
    assert passed_request.headers.get("x-user-id") == "user_admin"
    assert passed_request.headers.get("x-user-role") == "admin"
