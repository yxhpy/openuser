"""
Tests for Scheduler API endpoints.
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.api.main import create_app
from src.models.task import Task, TaskStatus, TaskType
from src.api.auth_utils import create_access_token


@pytest.fixture
def mock_user():
    """Create mock user."""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    user.is_active = True
    return user


@pytest.fixture
def auth_token(mock_user):
    """Create authentication token."""
    return create_access_token({"sub": mock_user.username, "user_id": mock_user.id})


@pytest.fixture
def sample_task(mock_user):
    """Sample task for testing."""
    task = Mock(spec=Task)
    task.id = 1
    task.user_id = mock_user.id
    task.name = "Test Task"
    task.description = "Test description"
    task.task_type = TaskType.VIDEO_GENERATION.value
    task.schedule = "0 0 * * *"
    task.params = {"key": "value"}
    task.status = TaskStatus.PENDING.value
    task.result = None
    task.error_message = None
    task.started_at = None
    task.completed_at = None
    task.created_at = datetime.now()
    task.updated_at = datetime.now()
    return task


@pytest.fixture
def mock_db_session(sample_task):
    """Create mock database session."""
    session = Mock(spec=Session)

    # Mock query chain
    query_mock = Mock()
    filter_mock = Mock()
    order_by_mock = Mock()

    query_mock.filter.return_value = filter_mock
    filter_mock.filter.return_value = filter_mock
    filter_mock.order_by.return_value = order_by_mock
    filter_mock.first.return_value = sample_task
    order_by_mock.all.return_value = [sample_task]

    session.query.return_value = query_mock
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    session.rollback = Mock()
    session.delete = Mock()

    return session


@pytest.fixture
def client(mock_user, mock_db_session):
    """Create test client with overridden dependencies."""
    app = create_app()

    def override_get_current_user():
        return mock_user

    def override_get_db():
        yield mock_db_session

    from src.api import scheduler
    from src.models import base
    app.dependency_overrides[scheduler.get_current_user] = override_get_current_user
    app.dependency_overrides[base.get_db] = override_get_db

    return TestClient(app)


def test_create_task(client, auth_token, mock_db_session, sample_task):
    """Test creating a new task."""
    def mock_refresh(task):
        task.id = 1
        task.created_at = datetime.now()
        task.updated_at = datetime.now()

    mock_db_session.refresh.side_effect = mock_refresh

    response = client.post(
        "/api/v1/scheduler/create",
        json={
            "name": "Test Task",
            "description": "Test description",
            "task_type": "video_generation",
            "schedule": "0 0 * * *",
            "params": {"key": "value"}
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["task_type"] == "video_generation"
    assert data["status"] == "pending"


def test_create_task_invalid_type(client, auth_token):
    """Test creating a task with invalid type."""
    response = client.post(
        "/api/v1/scheduler/create",
        json={
            "name": "Test Task",
            "task_type": "invalid_type",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert "Invalid task type" in response.json()["detail"]


def test_create_task_unauthorized():
    """Test creating a task without authentication."""
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/api/v1/scheduler/create",
        json={
            "name": "Test Task",
            "task_type": "video_generation",
        }
    )

    assert response.status_code == 401


def test_list_tasks(client, auth_token):
    """Test listing all tasks."""
    response = client.get(
        "/api/v1/scheduler/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert data["total"] == 1
    assert len(data["tasks"]) == 1


def test_list_tasks_with_status_filter(client, auth_token):
    """Test listing tasks with status filter."""
    response = client.get(
        "/api/v1/scheduler/list?task_status=pending",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


def test_list_tasks_with_type_filter(client, auth_token):
    """Test listing tasks with type filter."""
    response = client.get(
        "/api/v1/scheduler/list?task_type=video_generation",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


def test_list_tasks_invalid_status(client, auth_token):
    """Test listing tasks with invalid status."""
    response = client.get(
        "/api/v1/scheduler/list?task_status=invalid",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]


def test_list_tasks_invalid_type(client, auth_token):
    """Test listing tasks with invalid type."""
    response = client.get(
        "/api/v1/scheduler/list?task_type=invalid",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert "Invalid task type" in response.json()["detail"]


def test_get_task(client, auth_token):
    """Test getting task details."""
    response = client.get(
        "/api/v1/scheduler/1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test Task"


def test_get_task_not_found(client, auth_token, mock_db_session):
    """Test getting a non-existent task."""
    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = None
    mock_db_session.query.return_value = query_mock

    response = client.get(
        "/api/v1/scheduler/999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


def test_update_task(client, auth_token, mock_db_session, sample_task):
    """Test updating a task."""
    response = client.put(
        "/api/v1/scheduler/1",
        json={
            "name": "Updated Task",
            "status": "running"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1


def test_update_task_not_found(client, auth_token, mock_db_session):
    """Test updating a non-existent task."""
    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = None
    mock_db_session.query.return_value = query_mock

    response = client.put(
        "/api/v1/scheduler/999",
        json={
            "name": "Updated Task"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


def test_update_task_invalid_status(client, auth_token):
    """Test updating a task with invalid status."""
    response = client.put(
        "/api/v1/scheduler/1",
        json={
            "status": "invalid_status"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]


def test_delete_task(client, auth_token):
    """Test deleting a task."""
    response = client.delete(
        "/api/v1/scheduler/1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 204


def test_delete_task_not_found(client, auth_token, mock_db_session):
    """Test deleting a non-existent task."""
    query_mock = Mock()
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = None
    mock_db_session.query.return_value = query_mock

    response = client.delete(
        "/api/v1/scheduler/999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


def test_create_task_exception(client, auth_token, mock_db_session):
    """Test creating a task with exception."""
    mock_db_session.commit.side_effect = Exception("Database error")

    response = client.post(
        "/api/v1/scheduler/create",
        json={
            "name": "Test Task",
            "task_type": "video_generation",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 500
    assert "Failed to create task" in response.json()["detail"]


def test_list_tasks_exception(client, auth_token, mock_db_session):
    """Test listing tasks with exception."""
    mock_db_session.query.side_effect = Exception("Database error")

    response = client.get(
        "/api/v1/scheduler/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 500
    assert "Failed to list tasks" in response.json()["detail"]


def test_update_task_exception(client, auth_token, mock_db_session, sample_task):
    """Test updating a task with exception."""
    mock_db_session.commit.side_effect = Exception("Database error")

    response = client.put(
        "/api/v1/scheduler/1",
        json={
            "name": "Updated Task"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 500
    assert "Failed to update task" in response.json()["detail"]


def test_update_task_all_fields(client, auth_token, mock_db_session, sample_task):
    """Test updating all task fields."""
    response = client.put(
        "/api/v1/scheduler/1",
        json={
            "name": "Updated Task",
            "description": "Updated description",
            "schedule": "0 1 * * *",
            "params": {"new_key": "new_value"},
            "status": "running"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
