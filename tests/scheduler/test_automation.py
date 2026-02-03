"""
Tests for automation module.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy.orm import Session

from src.models.digital_human import DigitalHuman
from src.models.task import Task as TaskModel
from src.models.task import TaskStatus, TaskType
from src.models.user import User
from src.scheduler.automation import (
    BatchProcessor,
    CleanupManager,
    ReportGenerator,
    batch_processing,
    cleanup_maintenance,
    generate_daily_report,
    scheduled_video_generation,
)


@pytest.fixture
def mock_session():
    """Create mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def sample_user():
    """Create sample user."""
    user = User(id=1, username="testuser", email="test@example.com")
    return user


@pytest.fixture
def sample_digital_human(sample_user):
    """Create sample digital human."""
    dh = DigitalHuman(
        id=1,
        user_id=sample_user.id,
        name="Test DH",
        description="Test digital human",
        image_path="test.jpg",
        is_active=True,
    )
    return dh


@pytest.fixture
def sample_tasks(sample_user):
    """Create sample tasks."""
    now = datetime.utcnow()
    return [
        TaskModel(
            id=1,
            user_id=sample_user.id,
            name="Task 1",
            task_type=TaskType.VIDEO_GENERATION,
            status=TaskStatus.COMPLETED,
            created_at=now - timedelta(days=1),
            completed_at=now - timedelta(hours=23),
        ),
        TaskModel(
            id=2,
            user_id=sample_user.id,
            name="Task 2",
            task_type=TaskType.VOICE_SYNTHESIS,
            status=TaskStatus.FAILED,
            created_at=now - timedelta(days=1),
            completed_at=now - timedelta(hours=22),
        ),
        TaskModel(
            id=3,
            user_id=sample_user.id,
            name="Task 3",
            task_type=TaskType.VIDEO_GENERATION,
            status=TaskStatus.PENDING,
            created_at=now - timedelta(days=1),
        ),
    ]


class TestReportGenerator:
    """Test ReportGenerator class."""

    def test_generate_usage_report(self, mock_session, sample_tasks):
        """Test usage report generation."""
        # Setup mock
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.with_entities.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [
            (TaskStatus.COMPLETED, 1),
            (TaskStatus.FAILED, 1),
            (TaskStatus.PENDING, 1),
        ]
        mock_query.scalar.return_value = 1
        mock_query.count.return_value = 3
        mock_session.query.return_value = mock_query

        # Generate report
        report_gen = ReportGenerator(mock_session)
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow()

        report = report_gen.generate_usage_report(start_date, end_date)

        # Verify report structure
        assert "period" in report
        assert "tasks_by_status" in report
        assert "tasks_by_type" in report
        assert "active_users" in report
        assert "total_tasks" in report
        assert report["total_tasks"] == 3
        assert report["active_users"] == 1

    def test_generate_usage_report_with_user_filter(self, mock_session):
        """Test usage report with user filter."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.with_entities.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.scalar.return_value = 1
        mock_query.count.return_value = 0
        mock_session.query.return_value = mock_query

        report_gen = ReportGenerator(mock_session)
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow()

        report = report_gen.generate_usage_report(start_date, end_date, user_id=1)

        assert report["total_tasks"] == 0
        # Verify user_id filter was applied
        assert mock_query.filter.call_count >= 2

    def test_generate_tasks_report(self, mock_session, sample_tasks):
        """Test tasks report generation."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = sample_tasks
        mock_session.query.return_value = mock_query

        report_gen = ReportGenerator(mock_session)
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow()

        report = report_gen.generate_tasks_report(start_date, end_date)

        assert "period" in report
        assert "total_tasks" in report
        assert "tasks" in report
        assert report["total_tasks"] == 3
        assert len(report["tasks"]) == 3

    def test_generate_tasks_report_with_user_filter(self, mock_session, sample_tasks):
        """Test tasks report with user filter."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_tasks[0]]
        mock_session.query.return_value = mock_query

        report_gen = ReportGenerator(mock_session)
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow()

        report = report_gen.generate_tasks_report(start_date, end_date, user_id=1)

        assert report["total_tasks"] == 1
        # Verify user_id filter was applied
        assert mock_query.filter.call_count >= 2

    def test_generate_digital_humans_report_with_user_filter(
        self, mock_session, sample_digital_human
    ):
        """Test digital humans report with user filter."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sample_digital_human]
        mock_query.count.return_value = 1
        mock_session.query.return_value = mock_query

        report_gen = ReportGenerator(mock_session)
        report = report_gen.generate_digital_humans_report(user_id=1)

        assert report["total_digital_humans"] == 1
        # Verify user_id filter was applied
        mock_query.filter.assert_called()

    def test_generate_digital_humans_report(self, mock_session, sample_digital_human):
        """Test digital humans report generation."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sample_digital_human]
        mock_query.count.return_value = 1
        mock_session.query.return_value = mock_query

        report_gen = ReportGenerator(mock_session)
        report = report_gen.generate_digital_humans_report()

        assert "total_digital_humans" in report
        assert "active_digital_humans" in report
        assert "inactive_digital_humans" in report
        assert "digital_humans" in report
        assert report["total_digital_humans"] == 1
        assert report["active_digital_humans"] == 1


class TestBatchProcessor:
    """Test BatchProcessor class."""

    @patch("src.scheduler.tasks.video_generation_task")
    def test_process_video_generation_batch(self, mock_task, mock_session):
        """Test video generation batch processing."""
        mock_task.delay.return_value = Mock(id="celery-task-id")

        items = [
            {
                "user_id": 1,
                "digital_human_id": 1,
                "text": "Hello world",
                "mode": "enhanced_talking_head",
            }
        ]

        processor = BatchProcessor(mock_session)
        results = processor.process_video_generation_batch(items)

        assert len(results) == 1
        assert results[0]["status"] == "queued"
        assert "task_id" in results[0]
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called()
        mock_task.delay.assert_called_once()

    @patch("src.scheduler.tasks.voice_synthesis_task")
    def test_process_voice_synthesis_batch(self, mock_task, mock_session):
        """Test voice synthesis batch processing."""
        mock_task.delay.return_value = Mock(id="celery-task-id")

        items = [{"user_id": 1, "text": "Hello world", "backend": "coqui"}]

        processor = BatchProcessor(mock_session)
        results = processor.process_voice_synthesis_batch(items)

        assert len(results) == 1
        assert results[0]["status"] == "queued"
        mock_task.delay.assert_called_once()

    @patch("src.scheduler.tasks.video_generation_task")
    def test_batch_processing_with_error(self, mock_task, mock_session):
        """Test batch processing with error."""
        mock_session.add.side_effect = Exception("Database error")

        items = [{"user_id": 1, "digital_human_id": 1, "text": "Hello"}]

        processor = BatchProcessor(mock_session)
        results = processor.process_video_generation_batch(items)

        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert "error" in results[0]

    @patch("src.scheduler.tasks.voice_synthesis_task")
    def test_voice_synthesis_batch_with_error(self, mock_task, mock_session):
        """Test voice synthesis batch processing with error."""
        mock_session.add.side_effect = Exception("Database error")

        items = [{"user_id": 1, "text": "Hello"}]

        processor = BatchProcessor(mock_session)
        results = processor.process_voice_synthesis_batch(items)

        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert "error" in results[0]


class TestCleanupManager:
    """Test CleanupManager class."""

    def test_cleanup_old_tasks(self, mock_session):
        """Test cleanup of old tasks."""
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.delete.return_value = 5
        mock_session.query.return_value = mock_query

        cleanup_mgr = CleanupManager(mock_session)
        result = cleanup_mgr.cleanup_old_tasks(completed_days=30, failed_days=7)

        assert "completed_deleted" in result
        assert "failed_deleted" in result
        assert result["completed_deleted"] == 5
        assert result["failed_deleted"] == 5
        mock_session.commit.assert_called_once()

    def test_cleanup_temp_files(self, tmp_path):
        """Test cleanup of temporary files."""
        # Create temp directory with old files
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()

        # Create old file
        old_file = temp_dir / "old_file.txt"
        old_file.write_text("old content")

        # Set file modification time to 10 days ago
        import os
        import time

        old_time = time.time() - (10 * 24 * 60 * 60)
        os.utime(old_file, (old_time, old_time))

        # Create recent file
        recent_file = temp_dir / "recent_file.txt"
        recent_file.write_text("recent content")

        cleanup_mgr = CleanupManager(Mock())
        result = cleanup_mgr.cleanup_temp_files(temp_dir=str(temp_dir), days=7)

        assert result["files_deleted"] == 1
        assert result["bytes_freed"] > 0
        assert not old_file.exists()
        assert recent_file.exists()

    def test_cleanup_temp_files_nonexistent_dir(self):
        """Test cleanup with nonexistent directory."""
        cleanup_mgr = CleanupManager(Mock())
        result = cleanup_mgr.cleanup_temp_files(temp_dir="/nonexistent/path", days=7)

        assert result["files_deleted"] == 0
        assert result["bytes_freed"] == 0


class TestCeleryTasks:
    """Test Celery automation tasks."""

    @patch("src.scheduler.automation.DatabaseManager")
    @patch("src.scheduler.automation.ReportGenerator")
    def test_generate_daily_report(self, mock_report_gen_class, mock_db_manager, tmp_path):
        """Test daily report generation task."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.return_value.get_session.return_value = mock_session

        mock_report_gen = Mock()
        mock_report_gen.generate_usage_report.return_value = {"total_tasks": 10}
        mock_report_gen.generate_tasks_report.return_value = {"tasks": []}
        mock_report_gen.generate_digital_humans_report.return_value = {
            "total_digital_humans": 5
        }
        mock_report_gen_class.return_value = mock_report_gen

        # Change output directory to tmp_path
        with patch("src.scheduler.automation.Path") as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.__truediv__.return_value = tmp_path / "report.json"

            with patch("builtins.open", create=True) as mock_open:
                mock_file = Mock()
                mock_open.return_value.__enter__.return_value = mock_file

                result = generate_daily_report()

                assert "report_path" in result
                assert "date" in result
                mock_session.close.assert_called_once()

    @patch("src.scheduler.automation.DatabaseManager")
    @patch("src.scheduler.tasks.video_generation_task")
    def test_scheduled_video_generation(
        self, mock_video_task, mock_db_manager, sample_digital_human
    ):
        """Test scheduled video generation task."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.return_value.get_session.return_value = mock_session

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_digital_human
        mock_session.query.return_value = mock_query

        mock_video_task.delay.return_value = Mock(id="celery-task-id")

        result = scheduled_video_generation(
            digital_human_id=1, text="Hello world", mode="enhanced_talking_head"
        )

        assert "task_id" in result
        assert "celery_task_id" in result
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_video_task.delay.assert_called_once()

    @patch("src.scheduler.automation.DatabaseManager")
    @patch("src.scheduler.automation.BatchProcessor")
    def test_batch_processing_task(self, mock_batch_processor_class, mock_db_manager):
        """Test batch processing task."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.return_value.get_session.return_value = mock_session

        mock_processor = Mock()
        mock_processor.process_video_generation_batch.return_value = [
            {"status": "queued", "task_id": 1}
        ]
        mock_batch_processor_class.return_value = mock_processor

        items = [{"user_id": 1, "digital_human_id": 1, "text": "Hello"}]
        result = batch_processing(batch_type="video_generation", items=items)

        assert "batch_type" in result
        assert "total" in result
        assert "results" in result
        assert result["total"] == 1
        mock_processor.process_video_generation_batch.assert_called_once_with(items)

    @patch("src.scheduler.automation.DatabaseManager")
    @patch("src.scheduler.automation.BatchProcessor")
    def test_batch_processing_voice_synthesis(self, mock_batch_processor_class, mock_db_manager):
        """Test batch processing task for voice synthesis."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.return_value.get_session.return_value = mock_session

        mock_processor = Mock()
        mock_processor.process_voice_synthesis_batch.return_value = [
            {"status": "queued", "task_id": 1}
        ]
        mock_batch_processor_class.return_value = mock_processor

        items = [{"user_id": 1, "text": "Hello"}]
        result = batch_processing(batch_type="voice_synthesis", items=items)

        assert "batch_type" in result
        assert "total" in result
        assert "results" in result
        assert result["total"] == 1
        mock_processor.process_voice_synthesis_batch.assert_called_once_with(items)

    @patch("src.scheduler.automation.DatabaseManager")
    @patch("src.scheduler.automation.CleanupManager")
    def test_cleanup_maintenance_task(self, mock_cleanup_manager_class, mock_db_manager):
        """Test cleanup maintenance task."""
        # Setup mocks
        mock_session = Mock()
        mock_db_manager.return_value.get_session.return_value = mock_session

        mock_cleanup = Mock()
        mock_cleanup.cleanup_old_tasks.return_value = {
            "completed_deleted": 5,
            "failed_deleted": 3,
        }
        mock_cleanup.cleanup_temp_files.return_value = {"files_deleted": 10, "bytes_freed": 1024}
        mock_cleanup_manager_class.return_value = mock_cleanup

        result = cleanup_maintenance()

        assert "timestamp" in result
        assert "task_cleanup" in result
        assert "file_cleanup" in result
        assert result["task_cleanup"]["completed_deleted"] == 5
        assert result["file_cleanup"]["files_deleted"] == 10
        mock_cleanup.cleanup_old_tasks.assert_called_once()
        mock_cleanup.cleanup_temp_files.assert_called_once()

    @patch("src.scheduler.automation.DatabaseManager")
    def test_generate_daily_report_error(self, mock_db_manager):
        """Test daily report generation with error."""
        mock_session = Mock()
        mock_session.close = Mock()
        mock_db_manager.return_value.get_session.return_value = mock_session

        # Make ReportGenerator raise an error
        with patch("src.scheduler.automation.ReportGenerator") as mock_report_gen_class:
            mock_report_gen_class.side_effect = Exception("Report generation failed")

            with pytest.raises(Exception, match="Report generation failed"):
                generate_daily_report()

            mock_session.close.assert_called_once()

    @patch("src.scheduler.automation.DatabaseManager")
    def test_scheduled_video_generation_not_found(self, mock_db_manager):
        """Test scheduled video generation with nonexistent digital human."""
        mock_session = Mock()
        mock_db_manager.return_value.get_session.return_value = mock_session

        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Digital human not found
        mock_session.query.return_value = mock_query

        with pytest.raises(ValueError, match="Digital human .* not found"):
            scheduled_video_generation(digital_human_id=999, text="Hello")

        mock_session.close.assert_called_once()

    @patch("src.scheduler.automation.DatabaseManager")
    @patch("src.scheduler.automation.BatchProcessor")
    def test_batch_processing_unknown_type(self, mock_batch_processor_class, mock_db_manager):
        """Test batch processing with unknown type."""
        mock_session = Mock()
        mock_db_manager.return_value.get_session.return_value = mock_session

        with pytest.raises(ValueError, match="Unknown batch type"):
            batch_processing(batch_type="unknown_type", items=[])

        mock_session.close.assert_called_once()

    @patch("src.scheduler.automation.DatabaseManager")
    @patch("src.scheduler.automation.CleanupManager")
    def test_cleanup_maintenance_error(self, mock_cleanup_manager_class, mock_db_manager):
        """Test cleanup maintenance with error."""
        mock_session = Mock()
        mock_db_manager.return_value.get_session.return_value = mock_session

        mock_cleanup = Mock()
        mock_cleanup.cleanup_old_tasks.side_effect = Exception("Cleanup failed")
        mock_cleanup_manager_class.return_value = mock_cleanup

        with pytest.raises(Exception, match="Cleanup failed"):
            cleanup_maintenance()

        mock_session.close.assert_called_once()

    def test_cleanup_temp_files_with_error(self, tmp_path):
        """Test cleanup with file deletion error."""
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()

        # Create old file
        old_file = temp_dir / "old_file.txt"
        old_file.write_text("old content")

        # Set file modification time to 10 days ago
        import os
        import time

        old_time = time.time() - (10 * 24 * 60 * 60)
        os.utime(old_file, (old_time, old_time))

        # Make file read-only to cause deletion error
        old_file.chmod(0o444)
        temp_dir.chmod(0o555)

        cleanup_mgr = CleanupManager(Mock())
        result = cleanup_mgr.cleanup_temp_files(temp_dir=str(temp_dir), days=7)

        # Should handle error gracefully
        assert result["files_deleted"] == 0

        # Restore permissions for cleanup
        temp_dir.chmod(0o755)
        old_file.chmod(0o644)






