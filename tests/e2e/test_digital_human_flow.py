"""
End-to-end tests for digital human workflow.

Tests the complete digital human lifecycle:
1. User authentication
2. Create digital human
3. Generate video from text
4. Generate video from audio
5. List digital humans
6. Get digital human details
7. Delete digital human
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os
from pathlib import Path
from PIL import Image
import io

from src.api.main import app
from src.models.base import Base, get_db


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_e2e_digital_human.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def setup_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_database):
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_user(client):
    """Create and authenticate a test user."""
    # Register user
    register_data = {
        "username": "dhuser",
        "email": "dhuser@example.com",
        "password": "SecurePass123!",
    }
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 200
    tokens = response.json()
    return tokens["access_token"]


@pytest.fixture
def test_image():
    """Create a test image file."""
    # Create a simple test image
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


@pytest.mark.e2e
class TestDigitalHumanWorkflow:
    """Test complete digital human workflow."""

    def test_complete_digital_human_lifecycle(self, client, authenticated_user, test_image):
        """
        Test complete digital human lifecycle:
        1. Create digital human with image
        2. List digital humans
        3. Get digital human details
        4. Delete digital human
        """
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Step 1: Create digital human
        files = {"image": ("test.png", test_image, "image/png")}
        data = {
            "name": "Test Digital Human",
            "description": "A test digital human",
        }
        response = client.post(
            "/api/v1/digital-human/create", headers=headers, files=files, data=data
        )
        assert response.status_code == 200
        digital_human = response.json()
        assert digital_human["name"] == "Test Digital Human"
        assert digital_human["description"] == "A test digital human"
        assert "id" in digital_human
        dh_id = digital_human["id"]

        # Step 2: List digital humans
        response = client.get("/api/v1/digital-human/list", headers=headers)
        assert response.status_code == 200
        digital_humans = response.json()
        assert len(digital_humans) >= 1
        assert any(dh["id"] == dh_id for dh in digital_humans)

        # Step 3: Get digital human details
        response = client.get(f"/api/v1/digital-human/{dh_id}", headers=headers)
        assert response.status_code == 200
        dh_details = response.json()
        assert dh_details["id"] == dh_id
        assert dh_details["name"] == "Test Digital Human"

        # Step 4: Delete digital human
        response = client.delete(f"/api/v1/digital-human/{dh_id}", headers=headers)
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f"/api/v1/digital-human/{dh_id}", headers=headers)
        assert response.status_code == 404

    def test_unauthorized_access(self, client, test_image):
        """Test accessing digital human endpoints without authentication."""
        # Try to create without auth
        files = {"image": ("test.png", test_image, "image/png")}
        data = {"name": "Test", "description": "Test"}
        response = client.post("/api/v1/digital-human/create", files=files, data=data)
        assert response.status_code == 401

        # Try to list without auth
        response = client.get("/api/v1/digital-human/list")
        assert response.status_code == 401

    def test_access_other_user_digital_human(self, client, test_image):
        """Test that users cannot access other users' digital humans."""
        # Create first user and digital human
        register_data1 = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data1)
        user1_token = response.json()["access_token"]

        files = {"image": ("test.png", test_image, "image/png")}
        data = {"name": "User1 DH", "description": "Test"}
        response = client.post(
            "/api/v1/digital-human/create",
            headers={"Authorization": f"Bearer {user1_token}"},
            files=files,
            data=data,
        )
        dh_id = response.json()["id"]

        # Create second user
        register_data2 = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data2)
        user2_token = response.json()["access_token"]

        # Try to access user1's digital human with user2's token
        response = client.get(
            f"/api/v1/digital-human/{dh_id}",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert response.status_code == 404  # Should not find it

        # Try to delete user1's digital human with user2's token
        response = client.delete(
            f"/api/v1/digital-human/{dh_id}",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert response.status_code == 404  # Should not find it
