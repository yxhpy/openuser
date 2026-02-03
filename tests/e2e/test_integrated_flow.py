"""
End-to-end tests for integrated workflows.

Tests complex workflows that span multiple components:
1. Complete user journey from registration to video generation
2. Multi-component interactions
3. Error handling across components
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PIL import Image
import io

from src.api.main import app
from src.models.base import Base, get_db


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_e2e_integrated.db"
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
def test_image():
    """Create a test image file."""
    img = Image.new("RGB", (100, 100), color="blue")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


@pytest.mark.e2e
class TestIntegratedWorkflows:
    """Test integrated workflows across multiple components."""

    def test_complete_user_journey(self, client, test_image):
        """
        Test complete user journey:
        1. Register user
        2. Create digital human
        3. Create agent
        4. Create scheduled task
        5. List all resources
        6. Clean up all resources
        """
        # Step 1: Register user
        register_data = {
            "username": "journeyuser",
            "email": "journey@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Create digital human
        files = {"image": ("test.png", test_image, "image/png")}
        data = {"name": "Journey DH", "description": "Test digital human"}
        response = client.post(
            "/api/v1/digital-human/create", headers=headers, files=files, data=data
        )
        assert response.status_code == 200
        dh_id = response.json()["id"]

        # Step 3: Create agent
        agent_data = {
            "name": "journey-agent",
            "system_prompt": "You are a helpful assistant",
            "capabilities": ["chat"],
        }
        response = client.post("/api/v1/agents/create", headers=headers, json=agent_data)
        assert response.status_code == 200

        # Step 4: Create scheduled task
        task_data = {
            "name": "Journey Task",
            "task_type": "video_generation",
            "schedule": "0 0 * * *",
            "params": {"digital_human_id": dh_id},
        }
        response = client.post("/api/v1/scheduler/create", headers=headers, json=task_data)
        assert response.status_code == 200
        task_id = response.json()["id"]

        # Step 5: List all resources
        # List digital humans
        response = client.get("/api/v1/digital-human/list", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

        # List agents
        response = client.get("/api/v1/agents/list", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

        # List tasks
        response = client.get("/api/v1/scheduler/list", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

        # List plugins
        response = client.get("/api/v1/plugins/list", headers=headers)
        assert response.status_code == 200

        # Step 6: Clean up all resources
        client.delete(f"/api/v1/scheduler/{task_id}", headers=headers)
        client.delete("/api/v1/agents/journey-agent", headers=headers)
        client.delete(f"/api/v1/digital-human/{dh_id}", headers=headers)

    def test_error_propagation(self, client):
        """Test that errors propagate correctly across components."""
        # Try to create digital human without authentication
        response = client.post("/api/v1/digital-human/create")
        assert response.status_code == 401

        # Register and authenticate
        register_data = {
            "username": "erroruser",
            "email": "error@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to get non-existent digital human
        response = client.get("/api/v1/digital-human/99999", headers=headers)
        assert response.status_code == 404

        # Try to create task with invalid type
        task_data = {
            "name": "Invalid Task",
            "task_type": "invalid_type",
            "schedule": "0 0 * * *",
            "params": {},
        }
        response = client.post("/api/v1/scheduler/create", headers=headers, json=task_data)
        assert response.status_code == 422

    def test_concurrent_operations(self, client, test_image):
        """Test concurrent operations on different resources."""
        # Register user
        register_data = {
            "username": "concurrentuser",
            "email": "concurrent@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create multiple resources concurrently (simulated)
        # Create digital human
        files = {"image": ("test.png", test_image, "image/png")}
        data = {"name": "DH1", "description": "Test"}
        response1 = client.post(
            "/api/v1/digital-human/create", headers=headers, files=files, data=data
        )

        # Create agent
        agent_data = {"name": "agent1", "system_prompt": "Test", "capabilities": ["chat"]}
        response2 = client.post("/api/v1/agents/create", headers=headers, json=agent_data)

        # Create task
        task_data = {
            "name": "Task1",
            "task_type": "video_generation",
            "schedule": "0 0 * * *",
            "params": {},
        }
        response3 = client.post("/api/v1/scheduler/create", headers=headers, json=task_data)

        # All should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # Cleanup
        client.delete(f"/api/v1/digital-human/{response1.json()['id']}", headers=headers)
        client.delete("/api/v1/agents/agent1", headers=headers)
        client.delete(f"/api/v1/scheduler/{response3.json()['id']}", headers=headers)

    def test_resource_isolation(self, client, test_image):
        """Test that resources are properly isolated between users."""
        # Create two users
        user1_data = {
            "username": "isolationuser1",
            "email": "isolation1@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=user1_data)
        user1_token = response.json()["access_token"]

        user2_data = {
            "username": "isolationuser2",
            "email": "isolation2@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=user2_data)
        user2_token = response.json()["access_token"]

        # User 1 creates resources
        files = {"image": ("test.png", test_image, "image/png")}
        data = {"name": "User1 DH", "description": "Test"}
        response = client.post(
            "/api/v1/digital-human/create",
            headers={"Authorization": f"Bearer {user1_token}"},
            files=files,
            data=data,
        )
        user1_dh_id = response.json()["id"]

        # User 2 should not see User 1's resources
        response = client.get(
            "/api/v1/digital-human/list",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert response.status_code == 200
        user2_dhs = response.json()
        assert not any(dh["id"] == user1_dh_id for dh in user2_dhs)

        # User 2 should not be able to access User 1's resource
        response = client.get(
            f"/api/v1/digital-human/{user1_dh_id}",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert response.status_code == 404

        # Cleanup
        client.delete(
            f"/api/v1/digital-human/{user1_dh_id}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )

    def test_api_health_check(self, client):
        """Test API health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert "status" in health_data

    def test_api_root_endpoint(self, client):
        """Test API root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        root_data = response.json()
        assert "message" in root_data or "name" in root_data
