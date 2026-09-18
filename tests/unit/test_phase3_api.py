"""
Unit Tests for Phase 3 On-Target API endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_on_target_predict_api_success():
    """Verifies POST /api/v1/on-target/predict with 30-mer context."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "guides_30nt": [
                "CAGAAAAAAAAACACTGCAACAAGAGGGTA",
                "TTTTAAAAAACCTACCGTAAACTCGGGTCA"
            ]
        }
        response = await ac.post("/api/v1/on-target/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["total_evaluated"] == 2
        assert len(data["predictions"]) == 2
        assert "hybrid_score" in data["predictions"][0]
        assert 0.0 <= data["predictions"][0]["predicted_on_target_efficiency"] <= 1.0


@pytest.mark.asyncio
async def test_on_target_performance_api():
    """Verifies GET /api/v1/on-target/performance."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/on-target/performance")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "READY"
        assert "metadata" in data
        assert "CNN" in data["metadata"]["metrics"]
        assert "XGBoost" in data["metadata"]["metrics"]
        assert "Hybrid" in data["metadata"]["metrics"]


@pytest.mark.asyncio
async def test_on_target_insufficient_context_error():
    """Verifies that invalid context length produces HTTP 422 error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "guides_30nt": ["SHORT_SEQ"]
        }
        response = await ac.post("/api/v1/on-target/predict", json=payload)
        assert response.status_code == 422
        detail = response.json().get("detail", {})
        assert detail.get("error") == "INSUFFICIENT_SEQUENCE_CONTEXT"
