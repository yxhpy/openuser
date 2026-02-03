"""
Tests for schedule manager.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.scheduler.schedule_manager import ScheduleManager, get_schedule_manager
from src.models.task import Task as TaskModel, TaskStatus, TaskType
from src.models.base import DatabaseManager


class TestScheduleManager:
    """Test ScheduleManager class."""

    @pytest.fixture
    def mock_db_manager(self):
        """Create mock database manager."""
        db_manager = Mock(spec=DatabaseManager)
        session = MagicMock()
        db_manager.get_session.return_value = session
        return db_manager, session

    @pytest.fixture
    def mock_celery_app(self):
        """Create mock Celery app."""
        app = MagicMock()
        app.conf.beat_schedule = {}
        return app

    @pytest.fixture
    def schedule_manager(self, mock_celery_app, mock_db_manager):
        """Create ScheduleManager instance."""
        db_manager, _ = mock_db_manager
        return ScheduleManager(mock_celery_app, db_manager)

    def test_init(self, schedule_manager, mock_celery_app, mock_db_manager):
        """Test ScheduleManager initialization."""
        db_manager, _ = mock_db_manager
        assert schedule_manager.celery_app == mock_celery_app
        assert schedule_manager.db_manager == db_manager

    def test_create_schedule_success(self, schedule_manager, mock_db_manager):
        """Test creating a scheduled task."""
        _, session = mock_db_manager

        # Mock task creation
        task = TaskModel(
            id=1,
            user_id=1,
            name="Test Task",
            task_type=TaskType.VIDEO_GENERATION,
            schedule="0 2 * * *",
            params={"test": "value"},
            status=TaskStatus.PENDING,
        )
        session.add = Mock()
        session.commit = Mock()
        session.refresh = Mock(side_effect=lambda t: setattr(t, "id", 1))
        session.close = Mock()

        # Create schedule
        result = schedule_manager.create_schedule(
            user_id=1,
            name="Test Task",
            task_type=TaskType.VIDEO_GENERATION,
            schedule_expr="0 2 * * *",
            params={"test": "value"},
            description="Test description",
        )

        # Verify
        session.add.assert_called_once()
        session.commit.assert_called_once()
        session.close.assert_called_once()

    def test_create_schedule_invalid_cron(self, schedule_manager):
        """Test creating schedule with invalid cron expression."""
        with pytest.raises(ValueError, match="Invalid cron expression"):
            schedule_manager.create_schedule(
                user_id=1,
                name="Test Task",
                task_type=TaskType.VIDEO_GENERATION,
                schedule_expr="invalid cron",
                params={},
            )

    def test_update_schedule_success(self, schedule_manager, mock_db_manager):
        """Test updating a scheduled task."""
        _, session = mock_db_manager

        # Mock existing task
        task = TaskModel(
            id=1,
            user_id=1,
            name="Test Task",
            task_type=TaskType.VIDEO_GENERATION,
            schedule="0 2 * * *",
            params={"test": "value"},
            status=TaskStatus.PENDING,
        )
        session.query().filter().first.return_value = task
        session.commit = Mock()
        session.refresh = Mock()
        session.close = Mock()

        # Update schedule
        result = schedule_manager.update_schedule(
            task_id=1, schedule_expr="0 3 * * *", name="Updated Task"
        )

        # Verify
        assert task.schedule == "0 3 * * *"
        assert task.name == "Updated Task"
        session.commit.assert_called_once()
        session.close.assert_called_once()

    def test_update_schedule_not_found(self, schedule_manager, mock_db_manager):
        """Test updating non-existent task."""
        _, session = mock_db_manager
        session.query().filter().first.return_value = None
        session.close = Mock()

        with pytest.raises(ValueError, match="Task .* not found"):
            schedule_manager.update_schedule(task_id=999, schedule_expr="0 3 * * *")

        session.close.assert_called_once()

    def test_update_schedule_invalid_cron(self, schedule_manager, mock_db_manager):
        """Test updating schedule with invalid cron expression."""
        _, session = mock_db_manager

        task = TaskModel(id=1, schedule="0 2 * * *")
        session.query().filter().first.return_value = task
        session.close = Mock()

        with pytest.raises(ValueError, match="Invalid cron expression"):
            schedule_manager.update_schedule(task_id=1, schedule_expr="invalid")

        session.close.assert_called_once()

    def test_delete_schedule_success(self, schedule_manager, mock_db_manager):
        """Test deleting a scheduled task."""
        _, session = mock_db_manager

        task = TaskModel(id=1, name="Test Task", schedule="0 2 * * *")
        session.query().filter().first.return_value = task
        session.delete = Mock()
        session.commit = Mock()
        session.close = Mock()

        result = schedule_manager.delete_schedule(task_id=1)

        assert result is True
        session.delete.assert_called_once_with(task)
        session.commit.assert_called_once()
        session.close.assert_called_once()

    def test_delete_schedule_not_found(self, schedule_manager, mock_db_manager):
        """Test deleting non-existent task."""
        _, session = mock_db_manager
        session.query().filter().first.return_value = None
        session.close = Mock()

        with pytest.raises(ValueError, match="Task .* not found"):
            schedule_manager.delete_schedule(task_id=999)

        session.close.assert_called_once()

    def test_get_schedule(self, schedule_manager, mock_db_manager):
        """Test getting a scheduled task."""
        _, session = mock_db_manager

        task = TaskModel(id=1, name="Test Task")
        session.query().filter().first.return_value = task
        session.close = Mock()

        result = schedule_manager.get_schedule(task_id=1)

        assert result == task
        session.close.assert_called_once()

    def test_list_schedules_all(self, schedule_manager, mock_db_manager):
        """Test listing all scheduled tasks."""
        _, session = mock_db_manager

        tasks = [TaskModel(id=1, schedule="0 2 * * *"), TaskModel(id=2, schedule="0 3 * * *")]
        session.query().filter().all.return_value = tasks
        session.close = Mock()

        result = schedule_manager.list_schedules()

        assert result == tasks
        session.close.assert_called_once()

    def test_list_schedules_filtered(self, schedule_manager, mock_db_manager):
        """Test listing scheduled tasks with filters."""
        _, session = mock_db_manager

        tasks = [TaskModel(id=1, user_id=1, status=TaskStatus.PENDING, schedule="0 2 * * *")]
        query_mock = session.query().filter()
        query_mock.filter().filter().all.return_value = tasks
        session.close = Mock()

        result = schedule_manager.list_schedules(user_id=1, status=TaskStatus.PENDING)

        session.close.assert_called_once()

    def test_validate_cron_expression_valid(self, schedule_manager):
        """Test validating valid cron expressions."""
        assert schedule_manager.validate_cron_expression("0 2 * * *") is True
        assert schedule_manager.validate_cron_expression("*/5 * * * *") is True
        assert schedule_manager.validate_cron_expression("0 0 1 * *") is True
        assert schedule_manager.validate_cron_expression("0 0 * * 0") is True
        assert schedule_manager.validate_cron_expression("0-30 * * * *") is True
        assert schedule_manager.validate_cron_expression("0,15,30,45 * * * *") is True

    def test_validate_cron_expression_invalid(self, schedule_manager):
        """Test validating invalid cron expressions."""
        assert schedule_manager.validate_cron_expression("invalid") is False
        assert schedule_manager.validate_cron_expression("0 2 * *") is False  # Too few fields
        assert schedule_manager.validate_cron_expression("0 2 * * * *") is False  # Too many fields
        assert schedule_manager.validate_cron_expression("60 * * * *") is False  # Invalid minute
        assert schedule_manager.validate_cron_expression("* 24 * * *") is False  # Invalid hour
        assert schedule_manager.validate_cron_expression("* * 32 * *") is False  # Invalid day
        assert schedule_manager.validate_cron_expression("* * * 13 *") is False  # Invalid month
        assert schedule_manager.validate_cron_expression("* * * * 7") is False  # Invalid day of week

    def test_validate_cron_field_wildcard(self, schedule_manager):
        """Test validating wildcard cron field."""
        schedule_manager._validate_cron_field("*", 0, 59)  # Should not raise

    def test_validate_cron_field_range(self, schedule_manager):
        """Test validating range cron field."""
        schedule_manager._validate_cron_field("1-5", 0, 59)  # Should not raise

        with pytest.raises(ValueError):
            schedule_manager._validate_cron_field("60-65", 0, 59)

    def test_validate_cron_field_step(self, schedule_manager):
        """Test validating step cron field."""
        schedule_manager._validate_cron_field("*/5", 0, 59)  # Should not raise
        schedule_manager._validate_cron_field("10/5", 0, 59)  # Should not raise

        with pytest.raises(ValueError):
            schedule_manager._validate_cron_field("*/0", 0, 59)

    def test_validate_cron_field_list(self, schedule_manager):
        """Test validating list cron field."""
        schedule_manager._validate_cron_field("1,3,5", 0, 59)  # Should not raise

        with pytest.raises(ValueError):
            schedule_manager._validate_cron_field("1,60,5", 0, 59)

    def test_validate_cron_field_single_value(self, schedule_manager):
        """Test validating single value cron field."""
        schedule_manager._validate_cron_field("30", 0, 59)  # Should not raise

        with pytest.raises(ValueError):
            schedule_manager._validate_cron_field("60", 0, 59)

    def test_register_beat_schedule(self, schedule_manager, mock_celery_app):
        """Test registering task with Celery Beat."""
        task = TaskModel(
            id=1,
            task_type=TaskType.VIDEO_GENERATION,
            schedule="0 2 * * *",
            params={"key": "value"},
        )

        schedule_manager._register_beat_schedule(task)

        assert "scheduled_task_1" in mock_celery_app.conf.beat_schedule
        beat_task = mock_celery_app.conf.beat_schedule["scheduled_task_1"]
        assert beat_task["task"] == "src.scheduler.tasks.video_generation_task"

    def test_register_beat_schedule_no_schedule(self, schedule_manager, mock_celery_app):
        """Test registering task without schedule."""
        task = TaskModel(id=1, task_type=TaskType.VIDEO_GENERATION, schedule=None)

        schedule_manager._register_beat_schedule(task)

        assert "scheduled_task_1" not in mock_celery_app.conf.beat_schedule

    def test_unregister_beat_schedule(self, schedule_manager, mock_celery_app):
        """Test unregistering task from Celery Beat."""
        mock_celery_app.conf.beat_schedule["scheduled_task_1"] = {}
        task = TaskModel(id=1)

        schedule_manager._unregister_beat_schedule(task)

        assert "scheduled_task_1" not in mock_celery_app.conf.beat_schedule

    @patch("src.scheduler.schedule_manager.DatabaseManager")
    @patch("src.scheduler.schedule_manager.celery_app")
    def test_get_schedule_manager(self, mock_celery, mock_db_class):
        """Test get_schedule_manager function."""
        manager = get_schedule_manager()
        assert isinstance(manager, ScheduleManager)
