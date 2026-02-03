"""
End-to-end tests for authentication flow.

Tests the complete authentication workflow:
1. User registration
2. User login
3. Token refresh
4. Access protected endpoints
5. Token expiration handling
"""

import pytest
from datetime import timedelta
import uuid

from src.api.auth_utils import create_access_token


@pytest.mark.e2e
class TestAuthenticationFlow:
    """Test complete authentication workflow."""

    def test_complete_auth_flow(self, client):
        """
        Test complete authentication flow:
        1. Register new user
        2. Login with credentials
        3. Access protected endpoint
        4. Refresh token
        5. Access protected endpoint with new token
        """
        # Generate unique username
        unique_id = str(uuid.uuid4())[:8]

        # Step 1: Register new user
        register_data = {
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code in [200, 201]  # Accept both 200 and 201
        register_result = response.json()
        assert "access_token" in register_result
        assert "refresh_token" in register_result
        assert register_result["token_type"] == "bearer"

        # Step 2: Login with credentials
        login_data = {
            "username": register_data["username"],
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        login_result = response.json()
        assert "access_token" in login_result
        assert "refresh_token" in login_result
        access_token = login_result["access_token"]
        refresh_token = login_result["refresh_token"]

        # Step 3: Access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        user_info = response.json()
        assert user_info["username"] == register_data["username"]
        assert user_info["email"] == register_data["email"]

        # Step 4: Refresh token
        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        refresh_result = response.json()
        assert "access_token" in refresh_result
        new_access_token = refresh_result["access_token"]

        # Step 5: Access protected endpoint with new token
        headers = {"Authorization": f"Bearer {new_access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        user_info = response.json()
        assert user_info["username"] == register_data["username"]

    def test_invalid_credentials_flow(self, client):
        """Test authentication flow with invalid credentials."""
        unique_id = str(uuid.uuid4())[:8]

        # Register user
        register_data = {
            "username": f"testuser2_{unique_id}",
            "email": f"test2_{unique_id}@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code in [200, 201]

        # Try to login with wrong password
        login_data = {"username": register_data["username"], "password": "WrongPassword"}
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

        # Try to access protected endpoint without token
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_duplicate_registration(self, client):
        """Test registration with duplicate username/email."""
        unique_id = str(uuid.uuid4())[:8]

        # Register first user
        register_data = {
            "username": f"duplicate_{unique_id}",
            "email": f"duplicate_{unique_id}@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code in [200, 201]

        # Try to register with same username
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 400

    def test_invalid_token_flow(self, client):
        """Test accessing protected endpoints with invalid token."""
        # Try with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

        # Try with expired token
        expired_token = create_access_token(
            data={"sub": "testuser"}, expires_delta=timedelta(seconds=-1)
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

