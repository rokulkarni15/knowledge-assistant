import pytest
from fastapi.testclient import TestClient
from api_gateway.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Knowledge Assistant" in data["message"]

def test_service_discovery():
    """Test service discovery endpoint"""
    response = client.get("/api/v1/services")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data

def test_proxy_invalid_service():
    """Test proxy with invalid service returns 404"""
    response = client.get("/api/v1/invalid/test")
    assert response.status_code == 404