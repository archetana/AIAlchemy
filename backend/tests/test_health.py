"""
Health check and basic connectivity tests
"""

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint returns API information."""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["service"] == "AIAlchemy API"
    assert data["status"] == "running"
    assert "version" in data
    assert "api_endpoints" in data

@pytest.mark.asyncio 
async def test_health_endpoint(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "service" in data
    assert "database" in data
    assert data["service"] == "aialchemy-backend"

@pytest.mark.asyncio
async def test_api_status_endpoint(client: AsyncClient):
    """Test the API status endpoint."""
    response = await client.get("/api/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["api"] == "operational"
    assert "version" in data
    assert "available_endpoints" in data
    assert "auth" in data["available_endpoints"]
    assert "dashboard" in data["available_endpoints"]