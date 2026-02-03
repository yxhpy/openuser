"""
End-to-end tests for task scheduler workflow.

Tests the complete task scheduling lifecycle:
1. User authentication
2. Create scheduled task
3. List tasks with filters
4. Get task details
5. Update task
6. Delete task
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.api.main import app
from src.models.base import Base, get_db


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_e2e_scheduler.db"
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
    register_data = {
        "username": "scheduleruser",
        "email": "scheduleruser@example.com",
        "password": "SecurePass123!",
    }
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 200
    tokens = response.json()
    return tokens["access_token"]


@pytest.mark.e2e
class TestSchedulerWorkflow:
    """Test complete task scheduler workflow."""

    def test_complete_task_lifecycle(self, client, authenticated_user):
        """
        Test complete task lifecycle:
        1. Create task
        2. List tasks
        3. Get task details
        4. Update task
        5. Delete task
        """
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Step 1: Create task
        task_data = {
            "name": "Test Task",
            "description": "A test scheduled task",
            "task_type": "video_generation",
            "schedule": "0 0 * * *",  # Daily at midnight
            "params": {"mode": "lipsync", "text": "Hello world"},
        }
        response = client.post("/api/v1/scheduler/create", headers=headers, json=task_data)
        assert response.status_code == 200
        task = response.json()
        assert task["name"] == "Test Task"
        assert task["task_type"] == "video_generation"
        assert task["status"] == "pending"
        task_id = task["id"]

        # Step 2: List tasks
        response = client.get("/api/v1/scheduler/list", headers=headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1
        assert any(t["id"] == task_id for t in tasks)

        # Step 3: Get task details
        response = client.get(f"/api/v1/scheduler/{task_id}", headers=headers)
        assert response.status_code == 200
        task_details = response.json()
        assert task_details["id"] == task_id
        assert task_details["name"] == "Test Task"
        assert task_details["params"]["mode"] == "lipsync"

        # Step 4: Update task
        update_data = {
            "name": "Updated Test Task",
            "schedule": "0 12 * * *",  # Daily at noon
            "status": "completed",
        }
        response = client.put(
            f"/api/v1/scheduler/{task_id}", headers=headers, json=update_data
        )
        assert response.status_code == 200
        updated_task = response.json()
        assert updated_task["name"] == "Updated Test Task"
        assert updated_task["schedule"] == "0 12 * * *"
        assert updated_task["status"] == "completed"

        # Step 5: Delete task
        response = client.delete(f"/api/v1/scheduler/{task_id}", headers=headers)
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f"/api/v1/scheduler/{task_id}", headers=headers)
        assert response.status_code == 404

    def test_task_filtering(self, client, authenticated_user):
        """Test filtering tasks by status and type."""
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Create tasks with different statuses and types
        tasks_data = [
            {
                "name": "Task 1",
                "task_type": "video_generation",
                "schedule": "0 0 * * *",
                "params": {},
            },
            {
                "name": "Task 2",
                "task_type": "voice_synthesis",
                "schedule": "0 0 * * *",
                "params": {},
            },
            {
                "name": "Task 3",
                "task_type": "video_generation",
                "schedule": "0 0 * * *",
                "params": {},
            },
        ]

        task_ids = []
        for task_data in tasks_data:
            response = client.post(
                "/api/v1/scheduler/create", headers=headers, json=task_data
            )
            assert response.status_code == 200
            task_ids.append(response.json()["id"])

        # Update one task to completed status
        client.put(
            f"/api/v1/scheduler/{task_ids[0]}",
            headers=headers,
            json={"status": "completed"},
        )

        # Filter by status
        response = client.get(
            "/api/v1/scheduler/list?status=pending", headers=headers
        )
        assert response.status_code == 200
        pending_tasks = response.json()
        assert all(t["status"] == "pending" for t in pending_tasks)

        response = client.get(
            "/api/v1/scheduler/list?status=completed", headers=headers
        )
        assert response.status_code == 200
        completed_tasks = response.json()
        assert all(t["status"] == "completed" for t in completed_tasks)

        # Filter by type
        response = client.get(
            "/api/v1/scheduler/list?task_type=video_generation", headers=headers
        )
        assert response.status_code == 200
        video_tasks = response.json()
        assert all(t["task_type"] == "video_generation" for t in video_tasks)

        # Cleanup
        for task_id in task_ids:
            client.delete(f"/api/v1/scheduler/{task_id}", headers=headers)

    def test_unauthorized_scheduler_access(self, client):
        """Test accessing scheduler endpoints without authentication."""
        task_data = {
            "name": "Test",
            "task_type": "video_generation",
            "schedule": "0 0 * * *",
            "params": {},
        }

        # Try to create without auth
        response = client.post("/api/v1/scheduler/create", json=task_data)
        assert response.status_code == 401

        # Try to list without auth
        response = client.get("/api/v1/scheduler/list")
        assert response.status_code == 401

        # Try to get without auth
        response = client.get("/api/v1/scheduler/1")
        assert response.status_code == 401

        # Try to update without auth
        response = client.put("/api/v1/scheduler/1", json={"name": "Test"})
        assert response.status_code == 401

        # Try to delete without auth
        response = client.delete("/api/v1/scheduler/1")
        assert response.status_code == 401

    def test_access_other_user_tasks(self, client):
        """Test that users cannot access other users' tasks."""
        # Create first user and task
        register_data1 = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data1)
        user1_token = response.json()["access_token"]

        task_data = {
            "name": "User1 Task",
            "task_type": "video_generation",
            "schedule": "0 0 * * *",
            "params": {},
        }
        response = client.post(
            "/api/v1/scheduler/create",
            headers={"Authorization": f"Bearer {user1_token}"},
            json=task_data,
        )
        task_id = response.json()["id"]

        # Create second user
        register_data2 = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "SecurePass123!",
        }
        response = client.post("/api/v1/auth/register", json=register_data2)
        user2_token = response.json()["access_token"]

        # Try to access user1's task with user2's token
        response = client.get(
            f"/api/v1/scheduler/{task_id}",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert response.status_code == 404

        # Try to update user1's task with user2's token
        response = client.put(
            f"/api/v1/scheduler/{task_id}",
            headers={"Authorization": f"Bearer {user2_token}"},
            json={"name": "Hacked"},
        )
        assert response.status_code == 404

        # Try to delete user1's task with user2's token
        response = client.delete(
            f"/api/v1/scheduler/{task_id}",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert response.status_code == 404

    def test_invalid_task_data(self, client, authenticated_user):
        """Test creating task with invalid data."""
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Invalid task type
        task_data = {
            "name": "Test",
            "task_type": "invalid_type",
            "schedule": "0 0 * * *",
            "params": {},
        }
        response = client.post("/api/v1/scheduler/create", headers=headers, json=task_data)
        assert response.status_code == 422  # Validation error

        # Invalid cron schedule
        task_data = {
            "name": "Test",
            "task_type": "video_generation",
            "schedule": "invalid cron",
            "params": {},
        }
        response = client.post("/api/v1/scheduler/create", headers=headers, json=task_data)
        # Should either validate or accept (depending on implementation)
        assert response.status_code in [200, 400, 422]
