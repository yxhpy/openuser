"""
Tests for scheduler monitor API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.api.main import create_app
from src.models.user import User
from src.models.task import TaskStatus, TaskType


@pytest.fixture
def app():
    """Create FastAPI app."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_current_user():
    """Create mock current user."""
    user = User(id=1, username="testuser", email="test@example.com")
    return user


@pytest.fixture
def mock_monitor():
    """Create mock task monitor."""
    return Mock()


class TestSchedulerMonitorAPI:
    """Test scheduler monitor API endpoints."""

    def test_get_task_statistics(self, app, client, mock_current_user, mock_monitor):
        """Test GET /api/v1/scheduler/monitor/stats endpoint."""
        from src.api import scheduler_monitor

        # Override dependencies
        app.dependency_overrides[scheduler_monitor.get_current_user] = lambda: mock_current_user
        app.dependency_overrides[scheduler_monitor.get_task_monitor] = lambda: mock_monitor

        mock_monitor.get_task_stats.return_value = {
            "total": 100,
            "by_status": {
                "pending": 10,
                "running": 5,
                "completed": 70,
                "failed": 10,
                "cancelled": 5,
            },
            "by_type": {
                "video_generation": 40,
                "voice_synthesis": 30,
                "face_animation": 20,
                "report_generation": 5,
                "batch_processing": 5,
                "custom": 0,
            },
            "success_rate": 70.0,
        }

        response = client.get("/api/v1/scheduler/monitor/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 100
        assert data["success_rate"] == 70.0
        assert data["by_status"]["completed"] == 70

        # Clean up
        app.dependency_overrides.clear()

    def test_get_task_history(self, app, client, mock_current_user, mock_monitor):
        """Test GET /api/v1/scheduler/monitor/history endpoint."""
        from src.api import scheduler_monitor

        app.dependency_overrides[scheduler_monitor.get_current_user] = lambda: mock_current_user
        app.dependency_overrides[scheduler_monitor.get_task_monitor] = lambda: mock_monitor

        mock_monitor.get_task_history.return_value = [
            {
                "id": 1,
                "name": "Task 1",
                "task_type": "video_generation",
                "status": "completed",
                "created_at": "2024-01-01T00:00:00",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:01:00",
                "duration": 60.0,
                "error_message": None,
            }
        ]

        response = client.get("/api/v1/scheduler/monitor/history?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["id"] == 1
        assert data["limit"] == 10
        assert data["offset"] == 0

        app.dependency_overrides.clear()

    def test_get_task_history_with_filters(self, app, client, mock_current_user, mock_monitor):
        """Test GET /api/v1/scheduler/monitor/history with filters."""
        from src.api import scheduler_monitor

        app.dependency_overrides[scheduler_monitor.get_current_user] = lambda: mock_current_user
        app.dependency_overrides[scheduler_monitor.get_task_monitor] = lambda: mock_monitor

        mock_monitor.get_task_history.return_value = []

        response = client.get(
            "/api/v1/scheduler/monitor/history"
            "?task_type=video_generation&status=completed&limit=50&offset=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 0
        mock_monitor.get_task_history.assert_called_once()

        app.dependency_overrides.clear()

    def test_get_task_history_invalid_filter(self, app, client, mock_current_user, mock_monitor):
        """Test GET /api/v1/scheduler/monitor/history with invalid filter."""
        from src.api import scheduler_monitor

        app.dependency_overrides[scheduler_monitor.get_current_user] = lambda: mock_current_user
        app.dependency_overrides[scheduler_monitor.get_task_monitor] = lambda: mock_monitor

        response = client.get("/api/v1/scheduler/monitor/history?task_type=invalid_type")

        assert response.status_code == 400
        assert "Invalid filter value" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_get_recent_failures(self, app, client, mock_current_user, mock_monitor):
        """Test GET /api/v1/scheduler/monitor/failures endpoint."""
        from src.api import scheduler_monitor

        app.dependency_overrides[scheduler_monitor.get_current_user] = lambda: mock_current_user
        app.dependency_overrides[scheduler_monitor.get_task_monitor] = lambda: mock_monitor

        mock_monitor.get_recent_failures.return_value = [
            {
                "id": 1,
                "name": "Failed Task",
                "task_type": "video_generation",
                "error_message": "Test error",
                "completed_at": "2024-01-01T00:00:00",
            }
        ]

        response = client.get("/api/v1/scheduler/monitor/failures?hours=24&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data["failures"]) == 1
        assert data["failures"][0]["error_message"] == "Test error"

        app.dependency_overrides.clear()

    def test_get_performance_metrics(self, app, client, mock_current_user, mock_monitor):
        """Test GET /api/v1/scheduler/monitor/performance endpoint."""
        from src.api import scheduler_monitor

        app.dependency_overrides[scheduler_monitor.get_current_user] = lambda: mock_current_user
        app.dependency_overrides[scheduler_monitor.get_task_monitor] = lambda: mock_monitor

        mock_monitor.get_performance_metrics.return_value = {
            "total_tasks": 100,
            "avg_duration_seconds": 120.5,
            "success_rate": 85.0,
            "tasks_per_day": 14.3,
        }

        response = client.get("/api/v1/scheduler/monitor/performance?days=7")

        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 100
        assert data["avg_duration_seconds"] == 120.5
        assert data["success_rate"] == 85.0
        assert data["tasks_per_day"] == 14.3

        app.dependency_overrides.clear()

    def test_get_queue_status(self, app, client, mock_current_user, mock_monitor):
        """Test GET /api/v1/scheduler/monitor/queue endpoint."""
        from src.api import scheduler_monitor

        app.dependency_overrides[scheduler_monitor.get_current_user] = lambda: mock_current_user
        app.dependency_overrides[scheduler_monitor.get_task_monitor] = lambda: mock_monitor

        mock_monitor.get_queue_status.return_value = {
            "pending": 10,
            "running": 5,
            "pending_by_type": {
                "video_generation": 4,
                "voice_synthesis": 3,
                "face_animation": 2,
                "report_generation": 1,
                "batch_processing": 0,
                "custom": 0,
            },
        }

        response = client.get("/api/v1/scheduler/monitor/queue")

        assert response.status_code == 200
        data = response.json()
        assert data["pending"] == 10
        assert data["running"] == 5
        assert data["pending_by_type"]["video_generation"] == 4

        app.dependency_overrides.clear()

    def test_error_handling(self, app, client, mock_current_user, mock_monitor):
        """Test error handling in monitor endpoints."""
        from src.api import scheduler_monitor

        app.dependency_overrides[scheduler_monitor.get_current_user] = lambda: mock_current_user
        app.dependency_overrides[scheduler_monitor.get_task_monitor] = lambda: mock_monitor

        mock_monitor.get_task_stats.side_effect = Exception("Database error")

        response = client.get("/api/v1/scheduler/monitor/stats")

        assert response.status_code == 500
        assert "Failed to get task statistics" in response.json()["detail"]

        app.dependency_overrides.clear()
