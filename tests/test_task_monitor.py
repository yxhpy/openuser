"""
Tests for task monitor.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

from src.scheduler.monitor import TaskMonitor, get_task_monitor
from src.models.task import Task as TaskModel, TaskStatus, TaskType
from src.models.base import DatabaseManager


class TestTaskMonitor:
    """Test TaskMonitor class."""

    @pytest.fixture
    def mock_db_manager(self):
        """Create mock database manager."""
        db_manager = Mock(spec=DatabaseManager)
        session = MagicMock()
        db_manager.get_session.return_value = session
        return db_manager, session

    @pytest.fixture
    def task_monitor(self, mock_db_manager):
        """Create TaskMonitor instance."""
        db_manager, _ = mock_db_manager
        return TaskMonitor(db_manager)

    def test_init(self, task_monitor, mock_db_manager):
        """Test TaskMonitor initialization."""
        db_manager, _ = mock_db_manager
        assert task_monitor.db_manager == db_manager

    def test_get_task_stats(self, task_monitor, mock_db_manager):
        """Test getting task statistics."""
        _, session = mock_db_manager

        # Create a simple mock that returns counts
        with patch.object(task_monitor, 'db_manager') as mock_db:
            mock_session = MagicMock()
            mock_db.get_session.return_value = mock_session

            # Mock the query chain
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query

            # Total count
            mock_query.count.return_value = 100

            # Create filter mocks for status counts
            status_filters = []
            for count in [10, 5, 70, 10, 5]:  # pending, running, completed, failed, cancelled
                filter_mock = MagicMock()
                filter_mock.count.return_value = count
                status_filters.append(filter_mock)

            # Create filter mocks for type counts
            type_filters = []
            for count in [20, 30, 15, 25, 10, 0]:  # video, voice, face, report, batch, custom
                type_filter_mock = MagicMock()
                type_filter_mock.count.return_value = count
                filter_mock = MagicMock()
                filter_mock.filter.return_value = type_filter_mock
                type_filters.append(filter_mock)

            # Combine all filters
            all_filters = status_filters + type_filters
            mock_query.filter.side_effect = all_filters

            stats = task_monitor.get_task_stats()

            assert stats["total"] == 100
            assert stats["by_status"]["pending"] == 10
            assert stats["by_status"]["running"] == 5
            assert stats["by_status"]["completed"] == 70
            assert stats["by_status"]["failed"] == 10
            assert stats["by_status"]["cancelled"] == 5
            assert stats["success_rate"] == 70.0

    def test_get_task_stats_with_user_filter(self, task_monitor, mock_db_manager):
        """Test getting task statistics filtered by user."""
        _, session = mock_db_manager

        query_mock = session.query()
        query_mock.filter().count.return_value = 50
        query_mock.filter().filter().count.side_effect = [5, 2, 35, 5, 3] + [10] * 6

        session.close = Mock()

        stats = task_monitor.get_task_stats(user_id=1)

        assert stats["total"] == 50
        session.close.assert_called_once()

    def test_get_task_stats_empty(self, task_monitor, mock_db_manager):
        """Test getting task statistics with no tasks."""
        _, session = mock_db_manager

        query_mock = session.query()
        query_mock.count.return_value = 0
        query_mock.filter().count.return_value = 0
        query_mock.filter().filter().count.return_value = 0

        session.close = Mock()

        stats = task_monitor.get_task_stats()

        assert stats["total"] == 0
        assert stats["success_rate"] == 0.0
        session.close.assert_called_once()

    def test_get_task_history(self, task_monitor, mock_db_manager):
        """Test getting task history."""
        _, session = mock_db_manager

        # Mock tasks
        now = datetime.utcnow()
        tasks = [
            TaskModel(
                id=1,
                name="Task 1",
                task_type=TaskType.VIDEO_GENERATION,
                status=TaskStatus.COMPLETED,
                created_at=now,
                started_at=now,
                completed_at=now + timedelta(seconds=60),
                error_message=None,
            ),
            TaskModel(
                id=2,
                name="Task 2",
                task_type=TaskType.VOICE_SYNTHESIS,
                status=TaskStatus.FAILED,
                created_at=now,
                started_at=now,
                completed_at=now + timedelta(seconds=30),
                error_message="Test error",
            ),
        ]

        query_mock = session.query()
        query_mock.order_by().limit().offset().all.return_value = tasks
        session.close = Mock()

        history = task_monitor.get_task_history(limit=10, offset=0)

        assert len(history) == 2
        assert history[0]["id"] == 1
        assert history[0]["name"] == "Task 1"
        assert history[0]["status"] == "completed"
        assert history[0]["duration"] == 60.0
        assert history[1]["error_message"] == "Test error"
        session.close.assert_called_once()

    def test_get_task_history_with_filters(self, task_monitor, mock_db_manager):
        """Test getting task history with filters."""
        _, session = mock_db_manager

        query_mock = session.query()
        query_mock.filter().filter().filter().order_by().limit().offset().all.return_value = []
        session.close = Mock()

        history = task_monitor.get_task_history(
            user_id=1,
            task_type=TaskType.VIDEO_GENERATION,
            status=TaskStatus.COMPLETED,
            limit=50,
            offset=10,
        )

        assert len(history) == 0
        session.close.assert_called_once()

    def test_get_recent_failures(self, task_monitor, mock_db_manager):
        """Test getting recent failed tasks."""
        _, session = mock_db_manager

        now = datetime.utcnow()
        tasks = [
            TaskModel(
                id=1,
                name="Failed Task",
                task_type=TaskType.VIDEO_GENERATION,
                status=TaskStatus.FAILED,
                error_message="Test error",
                completed_at=now,
            )
        ]

        query_mock = session.query()
        query_mock.filter().filter().order_by().limit().all.return_value = tasks
        session.close = Mock()

        failures = task_monitor.get_recent_failures(hours=24, limit=10)

        assert len(failures) == 1
        assert failures[0]["id"] == 1
        assert failures[0]["error_message"] == "Test error"
        session.close.assert_called_once()

    def test_get_recent_failures_with_user_filter(self, task_monitor, mock_db_manager):
        """Test getting recent failures filtered by user."""
        _, session = mock_db_manager

        query_mock = session.query()
        query_mock.filter().filter().filter().order_by().limit().all.return_value = []
        session.close = Mock()

        failures = task_monitor.get_recent_failures(user_id=1, hours=48, limit=20)

        assert len(failures) == 0
        session.close.assert_called_once()

    def test_get_performance_metrics(self, task_monitor, mock_db_manager):
        """Test getting performance metrics."""
        _, session = mock_db_manager

        now = datetime.utcnow()
        tasks = [
            TaskModel(
                id=1,
                status=TaskStatus.COMPLETED,
                created_at=now - timedelta(days=1),
                started_at=now - timedelta(days=1),
                completed_at=now - timedelta(days=1) + timedelta(seconds=120),
            ),
            TaskModel(
                id=2,
                status=TaskStatus.COMPLETED,
                created_at=now - timedelta(days=2),
                started_at=now - timedelta(days=2),
                completed_at=now - timedelta(days=2) + timedelta(seconds=180),
            ),
            TaskModel(
                id=3,
                status=TaskStatus.FAILED,
                created_at=now - timedelta(days=3),
            ),
        ]

        query_mock = session.query()
        query_mock.filter().all.return_value = tasks
        session.close = Mock()

        metrics = task_monitor.get_performance_metrics(days=7)

        assert metrics["total_tasks"] == 3
        assert metrics["avg_duration_seconds"] == 150.0  # (120 + 180) / 2
        assert metrics["success_rate"] == pytest.approx(66.67, rel=0.01)
        assert metrics["tasks_per_day"] == pytest.approx(0.43, rel=0.01)
        session.close.assert_called_once()

    def test_get_performance_metrics_no_tasks(self, task_monitor, mock_db_manager):
        """Test getting performance metrics with no tasks."""
        _, session = mock_db_manager

        query_mock = session.query()
        query_mock.filter().all.return_value = []
        session.close = Mock()

        metrics = task_monitor.get_performance_metrics(days=7)

        assert metrics["total_tasks"] == 0
        assert metrics["avg_duration_seconds"] == 0
        assert metrics["success_rate"] == 0
        assert metrics["tasks_per_day"] == 0
        session.close.assert_called_once()

    def test_get_performance_metrics_with_user_filter(self, task_monitor, mock_db_manager):
        """Test getting performance metrics filtered by user."""
        _, session = mock_db_manager

        query_mock = session.query()
        query_mock.filter().filter().all.return_value = []
        session.close = Mock()

        metrics = task_monitor.get_performance_metrics(user_id=1, days=30)

        assert metrics["total_tasks"] == 0
        session.close.assert_called_once()

    def test_get_queue_status(self, task_monitor, mock_db_manager):
        """Test getting queue status."""
        _, session = mock_db_manager

        query_mock = session.query()
        query_mock.filter().count.return_value = 10  # pending
        query_mock.filter().count.return_value = 5  # running

        # Mock pending by type
        query_mock.filter().filter().count.side_effect = [2, 3, 1, 2, 2, 0]

        session.close = Mock()

        status = task_monitor.get_queue_status()

        assert "pending" in status
        assert "running" in status
        assert "pending_by_type" in status
        session.close.assert_called_once()

    def test_calculate_duration(self, task_monitor):
        """Test calculating task duration."""
        now = datetime.utcnow()
        task = TaskModel(
            started_at=now, completed_at=now + timedelta(seconds=120)
        )

        duration = task_monitor._calculate_duration(task)

        assert duration == 120.0

    def test_calculate_duration_no_times(self, task_monitor):
        """Test calculating duration with missing times."""
        task = TaskModel(started_at=None, completed_at=None)

        duration = task_monitor._calculate_duration(task)

        assert duration is None

    def test_calculate_duration_only_started(self, task_monitor):
        """Test calculating duration with only start time."""
        task = TaskModel(started_at=datetime.utcnow(), completed_at=None)

        duration = task_monitor._calculate_duration(task)

        assert duration is None

    @patch("src.scheduler.monitor.DatabaseManager")
    def test_get_task_monitor(self, mock_db_class):
        """Test get_task_monitor function."""
        monitor = get_task_monitor()
        assert isinstance(monitor, TaskMonitor)
