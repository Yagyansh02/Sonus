"""
Tests for the health endpoint.
"""

import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked dependencies."""
    from app.main import app
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /api/health."""

    @patch("app.api.health.get_neo4j_session")
    def test_health_returns_200(self, mock_session, client):
        """Health endpoint should return 200 with status information."""
        # Mock the Neo4j session
        mock_neo4j = AsyncMock()
        mock_result = AsyncMock()
        mock_result.single = AsyncMock(return_value={"ping": 1})
        mock_neo4j.run = AsyncMock(return_value=mock_result)

        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "services" in data

    def test_health_response_structure(self, client):
        """Health response should contain expected fields."""
        response = client.get("/api/health")
        data = response.json()

        assert isinstance(data.get("services"), dict)
        assert "neo4j" in data["services"]
        assert "vector_store" in data["services"]
