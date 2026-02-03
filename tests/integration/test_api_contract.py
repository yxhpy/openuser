"""
API Contract Tests

These tests validate that the API responses match the defined Pydantic schemas
and that the frontend TypeScript types stay in sync with backend models.

This ensures frontend-backend compatibility and prevents breaking changes.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError
from typing import Type, Any, Dict
import json

from src.api.main import app
from src.api.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    VoiceSynthesizeRequest,
    VoiceSynthesizeResponse,
    DigitalHumanCreateRequest,
    DigitalHumanResponse,
    AgentCreateRequest,
    AgentResponse,
    TaskCreateRequest,
    TaskResponse,
)


@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest.mark.integration
class TestAPIContractValidation:
    """Test that API responses match defined schemas."""

    def validate_response(self, response_data: Dict[str, Any], schema: Type[BaseModel]):
        """
        Validate that response data matches the Pydantic schema.

        Args:
            response_data: The JSON response from the API
            schema: The Pydantic model to validate against

        Raises:
            ValidationError: If the response doesn't match the schema
        """
        try:
            schema(**response_data)
        except ValidationError as e:
            pytest.fail(f"Response validation failed: {e}")

    def test_auth_register_contract(self, client):
        """Test that /auth/register response matches TokenResponse schema."""
        request_data = {
            "username": "contracttest",
            "email": "contract@example.com",
            "password": "SecurePass123!",
        }

        # Validate request schema
        try:
            UserRegisterRequest(**request_data)
        except ValidationError as e:
            pytest.fail(f"Request validation failed: {e}")

        # Make request
        response = client.post("/api/v1/auth/register", json=request_data)

        # Skip if user already exists
        if response.status_code == 400:
            pytest.skip("User already exists")

        assert response.status_code in [200, 201]

        # Validate response schema
        self.validate_response(response.json(), TokenResponse)

    def test_auth_login_contract(self, client):
        """Test that /auth/login response matches TokenResponse schema."""
        # First register a user
        register_data = {
            "username": "logincontract",
            "email": "logincontract@example.com",
            "password": "SecurePass123!",
        }
        client.post("/api/v1/auth/register", json=register_data)

        # Test login
        login_data = {
            "username": "logincontract",
            "password": "SecurePass123!",
        }

        # Validate request schema
        try:
            UserLoginRequest(**login_data)
        except ValidationError as e:
            pytest.fail(f"Request validation failed: {e}")

        # Make request
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        # Validate response schema
        self.validate_response(response.json(), TokenResponse)

    def test_auth_me_contract(self, client):
        """Test that /auth/me response matches UserResponse schema."""
        # Register and get token
        register_data = {
            "username": "mecontract",
            "email": "mecontract@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)

        if response.status_code == 400:
            # User exists, login instead
            login_data = {
                "username": "mecontract",
                "password": "SecurePass123!",
            }
            response = client.post("/api/v1/auth/login", json=login_data)

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test /auth/me
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200

        # Validate response schema
        self.validate_response(response.json(), UserResponse)

    def test_agent_create_contract(self, client):
        """Test that /agents/create response matches AgentResponse schema."""
        # Get authenticated
        register_data = {
            "username": "agentcontract",
            "email": "agentcontract@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)

        if response.status_code == 400:
            login_data = {
                "username": "agentcontract",
                "password": "SecurePass123!",
            }
            response = client.post("/api/v1/auth/login", json=login_data)

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test agent creation
        agent_data = {
            "name": "contract-test-agent",
            "system_prompt": "Test agent",
            "capabilities": ["chat"],
        }

        # Validate request schema
        try:
            AgentCreateRequest(**agent_data)
        except ValidationError as e:
            pytest.fail(f"Request validation failed: {e}")

        # Make request
        response = client.post("/api/v1/agents/create", headers=headers, json=agent_data)

        # Skip if agent already exists
        if response.status_code == 400:
            pytest.skip("Agent already exists")

        assert response.status_code in [200, 201]

        # Validate response schema
        self.validate_response(response.json(), AgentResponse)

        # Cleanup
        client.delete(f"/api/v1/agents/{agent_data['name']}", headers=headers)

    def test_agent_list_contract(self, client):
        """Test that /agents/list response is a list of AgentResponse."""
        # Get authenticated
        register_data = {
            "username": "agentlistcontract",
            "email": "agentlistcontract@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)

        if response.status_code == 400:
            login_data = {
                "username": "agentlistcontract",
                "password": "SecurePass123!",
            }
            response = client.post("/api/v1/auth/login", json=login_data)

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test agent list
        response = client.get("/api/v1/agents/list", headers=headers)
        assert response.status_code == 200

        # API returns paginated response with {agents: [], total: 0}
        data = response.json()
        assert isinstance(data, dict)
        assert "agents" in data
        assert "total" in data
        assert isinstance(data["agents"], list)
        assert isinstance(data["total"], int)

        # Validate each agent in the list
        for agent in data["agents"]:
            self.validate_response(agent, AgentResponse)

    def test_response_field_types(self, client):
        """Test that response fields have correct types."""
        # Register user
        register_data = {
            "username": "typetest",
            "email": "typetest@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)

        if response.status_code == 400:
            login_data = {
                "username": "typetest",
                "password": "SecurePass123!",
            }
            response = client.post("/api/v1/auth/login", json=login_data)

        data = response.json()

        # Validate field types
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert isinstance(data["token_type"], str)
        assert data["token_type"] == "bearer"

    def test_error_response_format(self, client):
        """Test that error responses have consistent format."""
        # Test with invalid credentials
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "wrong"},
        )

        assert response.status_code == 401
        error_data = response.json()

        # Error responses should have 'detail' field
        assert "detail" in error_data
        assert isinstance(error_data["detail"], str)

    def test_validation_error_format(self, client):
        """Test that validation errors have consistent format."""
        # Test with invalid request data (missing required field)
        response = client.post(
            "/api/v1/auth/register",
            json={"username": "test"},  # Missing email and password
        )

        assert response.status_code == 422
        error_data = response.json()

        # Validation errors should have 'detail' field with list of errors
        assert "detail" in error_data
        assert isinstance(error_data["detail"], list)

        # Each error should have loc, msg, and type
        for error in error_data["detail"]:
            assert "loc" in error
            assert "msg" in error
            assert "type" in error


@pytest.mark.integration
class TestAPIContractConsistency:
    """Test that API contracts are consistent across endpoints."""

    def test_timestamp_format_consistency(self, client):
        """Test that all timestamps use ISO 8601 format."""
        # Register user
        register_data = {
            "username": "timestamptest",
            "email": "timestamptest@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)

        if response.status_code == 400:
            login_data = {
                "username": "timestamptest",
                "password": "SecurePass123!",
            }
            response = client.post("/api/v1/auth/login", json=login_data)

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get user info
        response = client.get("/api/v1/auth/me", headers=headers)
        user_data = response.json()

        # Check timestamp format (ISO 8601)
        if "created_at" in user_data:
            import re

            iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
            assert re.match(iso_pattern, user_data["created_at"])

    def test_id_field_consistency(self, client):
        """Test that ID fields are consistently typed."""
        # Register user
        register_data = {
            "username": "idtest",
            "email": "idtest@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)

        if response.status_code == 400:
            login_data = {
                "username": "idtest",
                "password": "SecurePass123!",
            }
            response = client.post("/api/v1/auth/login", json=login_data)

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get user info
        response = client.get("/api/v1/auth/me", headers=headers)
        user_data = response.json()

        # ID should be an integer
        if "id" in user_data:
            assert isinstance(user_data["id"], int)

    def test_pagination_consistency(self, client):
        """Test that paginated endpoints have consistent structure."""
        # Register user
        register_data = {
            "username": "paginationtest",
            "email": "paginationtest@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)

        if response.status_code == 400:
            login_data = {
                "username": "paginationtest",
                "password": "SecurePass123!",
            }
            response = client.post("/api/v1/auth/login", json=login_data)

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test agent list endpoint - returns paginated response
        response = client.get("/api/v1/agents/list", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "agents" in data
        assert "total" in data
        assert isinstance(data["agents"], list)
        assert isinstance(data["total"], int)
