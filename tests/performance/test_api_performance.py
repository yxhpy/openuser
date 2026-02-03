"""
Performance benchmark tests for API endpoints.

These tests measure the performance of critical API endpoints to ensure
they meet performance requirements.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for protected endpoints."""
    # Register a test user
    register_data = {
        "username": "perftest",
        "email": "perftest@example.com",
        "password": "TestPass123!",
    }
    client.post("/api/v1/auth/register", json=register_data)

    # Login to get token
    login_data = {"username": "perftest", "password": "TestPass123!"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.mark.performance
class TestAPIPerformance:
    """Performance benchmark tests for API endpoints."""

    def test_health_check_performance(self, benchmark, client):
        """Benchmark health check endpoint."""

        def health_check():
            response = client.get("/health")
            assert response.status_code == 200
            return response

        result = benchmark(health_check)
        assert result.status_code == 200

    def test_root_endpoint_performance(self, benchmark, client):
        """Benchmark root endpoint."""

        def root_endpoint():
            response = client.get("/")
            assert response.status_code == 200
            return response

        result = benchmark(root_endpoint)
        assert result.status_code == 200
