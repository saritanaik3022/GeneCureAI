"""
Tests for /api/health and /api/v1/health endpoints.
"""
import pytest


@pytest.mark.asyncio
async def test_direct_health_endpoint(async_client):
    """Test GET /api/health returns valid status and service identifier."""
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "gene-cure-ai"
    assert "execution_mode" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_v1_health_endpoint(async_client):
    """Test GET /api/v1/health returns valid status."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "gene-cure-ai"


@pytest.mark.asyncio
async def test_root_endpoint(async_client):
    """Test GET / returns metadata and scientific disclaimer."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "disclaimer" in data
    assert "Gene-Cure AI" in data["name"]
