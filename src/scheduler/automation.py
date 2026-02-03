"""
Automation features for OpenUser.

This module provides automated tasks for:
- Daily report generation
- Scheduled video generation
- Batch processing
- Cleanup and maintenance
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.base import DatabaseManager
from src.models.digital_human import DigitalHuman
from src.models.task import Task as TaskModel
from src.models.task import TaskStatus, TaskType
from src.models.user import User
from src.scheduler.celery_app import celery_app

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate various types of reports."""

    def __init__(self, session: Session):
        """
        Initialize report generator.

        Args:
            session: Database session
        """
        self.session = session

    def generate_usage_report(
        self, start_date: datetime, end_date: datetime, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate usage statistics report.

        Args:
            start_date: Report start date
            end_date: Report end date
            user_id: Optional user ID to filter by

        Returns:
            Dict with usage statistics
        """
        query = self.session.query(TaskModel).filter(
            TaskModel.created_at >= start_date, TaskModel.created_at <= end_date
        )

        if user_id:
            query = query.filter(TaskModel.user_id == user_id)

        # Total tasks by status
        tasks_by_status = (
            query.with_entities(TaskModel.status, func.count(TaskModel.id))
            .group_by(TaskModel.status)
            .all()
        )

        # Total tasks by type
        tasks_by_type = (
            query.with_entities(TaskModel.task_type, func.count(TaskModel.id))
            .group_by(TaskModel.task_type)
            .all()
        )

        # Active users
        active_users = query.with_entities(func.count(func.distinct(TaskModel.user_id))).scalar()

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "tasks_by_status": {str(status): count for status, count in tasks_by_status},
            "tasks_by_type": {str(task_type): count for task_type, count in tasks_by_type},
            "active_users": active_users,
            "total_tasks": query.count(),
        }

    def generate_tasks_report(
        self, start_date: datetime, end_date: datetime, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate task history report.

        Args:
            start_date: Report start date
            end_date: Report end date
            user_id: Optional user ID to filter by

        Returns:
            Dict with task history
        """
        query = self.session.query(TaskModel).filter(
            TaskModel.created_at >= start_date, TaskModel.created_at <= end_date
        )

        if user_id:
            query = query.filter(TaskModel.user_id == user_id)

        tasks = query.order_by(TaskModel.created_at.desc()).all()

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_tasks": len(tasks),
            "tasks": [
                {
                    "id": task.id,
                    "name": task.name,
                    "type": str(task.task_type),
                    "status": str(task.status),
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                }
                for task in tasks
            ],
        }

    def generate_digital_humans_report(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate digital humans report.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            Dict with digital humans statistics
        """
        query = self.session.query(DigitalHuman)

        if user_id:
            query = query.filter(DigitalHuman.user_id == user_id)

        digital_humans = query.all()
        active_count = query.filter(DigitalHuman.is_active == True).count()

        return {
            "total_digital_humans": len(digital_humans),
            "active_digital_humans": active_count,
            "inactive_digital_humans": len(digital_humans) - active_count,
            "digital_humans": [
                {
                    "id": dh.id,
                    "name": dh.name,
                    "description": dh.description,
                    "is_active": dh.is_active,
                    "created_at": dh.created_at.isoformat() if dh.created_at else None,
                }
                for dh in digital_humans
            ],
        }


class BatchProcessor:
    """Process multiple items in batch."""

    def __init__(self, session: Session):
        """
        Initialize batch processor.

        Args:
            session: Database session
        """
        self.session = session

    def process_video_generation_batch(
        self, items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process video generation batch.

        Args:
            items: List of video generation requests

        Returns:
            List of results
        """
        from src.scheduler.tasks import video_generation_task

        results = []
        for item in items:
            try:
                # Create task in database
                task = TaskModel(
                    user_id=item["user_id"],
                    name=f"Batch video generation - {item.get('name', 'Unnamed')}",
                    task_type=TaskType.VIDEO_GENERATION,
                    params=item,
                    status=TaskStatus.PENDING,
                )
                self.session.add(task)
                self.session.commit()

                # Queue Celery task
                video_generation_task.delay(
                    task_id=task.id,
                    digital_human_id=item["digital_human_id"],
                    text=item.get("text"),
                    audio_path=item.get("audio_path"),
                    mode=item.get("mode", "enhanced_talking_head"),
                )

                results.append({"item": item, "status": "queued", "task_id": task.id})
            except Exception as e:
                logger.error(f"Failed to queue video generation: {e}")
                results.append({"item": item, "status": "failed", "error": str(e)})

        return results

    def process_voice_synthesis_batch(
        self, items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process voice synthesis batch.

        Args:
            items: List of voice synthesis requests

        Returns:
            List of results
        """
        from src.scheduler.tasks import voice_synthesis_task

        results = []
        for item in items:
            try:
                # Create task in database
                task = TaskModel(
                    user_id=item["user_id"],
                    name=f"Batch voice synthesis - {item.get('name', 'Unnamed')}",
                    task_type=TaskType.VOICE_SYNTHESIS,
                    params=item,
                    status=TaskStatus.PENDING,
                )
                self.session.add(task)
                self.session.commit()

                # Queue Celery task
                voice_synthesis_task.delay(
                    task_id=task.id,
                    text=item["text"],
                    backend=item.get("backend", "coqui"),
                    speaker_wav=item.get("speaker_wav"),
                )

                results.append({"item": item, "status": "queued", "task_id": task.id})
            except Exception as e:
                logger.error(f"Failed to queue voice synthesis: {e}")
                results.append({"item": item, "status": "failed", "error": str(e)})

        return results


class CleanupManager:
    """Manage cleanup and maintenance tasks."""

    def __init__(self, session: Session):
        """
        Initialize cleanup manager.

        Args:
            session: Database session
        """
        self.session = session

    def cleanup_old_tasks(
        self, completed_days: int = 30, failed_days: int = 7
    ) -> Dict[str, int]:
        """
        Cleanup old tasks from database.

        Args:
            completed_days: Days to keep completed tasks
            failed_days: Days to keep failed tasks

        Returns:
            Dict with cleanup statistics
        """
        now = datetime.utcnow()
        completed_threshold = now - timedelta(days=completed_days)
        failed_threshold = now - timedelta(days=failed_days)

        # Delete old completed tasks
        completed_deleted = (
            self.session.query(TaskModel)
            .filter(
                TaskModel.status == TaskStatus.COMPLETED,
                TaskModel.completed_at < completed_threshold,
            )
            .delete()
        )

        # Delete old failed tasks
        failed_deleted = (
            self.session.query(TaskModel)
            .filter(
                TaskModel.status == TaskStatus.FAILED, TaskModel.completed_at < failed_threshold
            )
            .delete()
        )

        self.session.commit()

        logger.info(
            f"Cleaned up {completed_deleted} completed tasks and {failed_deleted} failed tasks"
        )

        return {"completed_deleted": completed_deleted, "failed_deleted": failed_deleted}

    def cleanup_temp_files(self, temp_dir: str = "outputs/temp", days: int = 7) -> Dict[str, int]:
        """
        Cleanup temporary files older than specified days.

        Args:
            temp_dir: Temporary directory path
            days: Days to keep temporary files

        Returns:
            Dict with cleanup statistics
        """
        import os
        import shutil

        temp_path = Path(temp_dir)
        if not temp_path.exists():
            return {"files_deleted": 0, "bytes_freed": 0}

        now = datetime.utcnow()
        threshold = now - timedelta(days=days)
        files_deleted = 0
        bytes_freed = 0

        for file_path in temp_path.rglob("*"):
            if file_path.is_file():
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime < threshold:
                    file_size = file_path.stat().st_size
                    try:
                        file_path.unlink()
                        files_deleted += 1
                        bytes_freed += file_size
                    except Exception as e:
                        logger.error(f"Failed to delete {file_path}: {e}")

        logger.info(f"Cleaned up {files_deleted} temp files, freed {bytes_freed} bytes")

        return {"files_deleted": files_deleted, "bytes_freed": bytes_freed}


# Celery tasks for automation

@celery_app.task(name="src.scheduler.automation.generate_daily_report")
def generate_daily_report() -> Dict[str, Any]:
    """
    Generate daily usage report.

    This task runs daily to generate usage statistics for the previous day.

    Returns:
        Dict with report path and metadata
    """
    import os

    database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/openuser")
    db_manager = DatabaseManager(database_url)
    session = db_manager.get_session()

    try:
        # Generate report for yesterday
        end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=1)

        report_gen = ReportGenerator(session)
        usage_report = report_gen.generate_usage_report(start_date, end_date)
        tasks_report = report_gen.generate_tasks_report(start_date, end_date)
        digital_humans_report = report_gen.generate_digital_humans_report()

        # Combine reports
        daily_report = {
            "date": start_date.date().isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "usage": usage_report,
            "tasks": tasks_report,
            "digital_humans": digital_humans_report,
        }

        # Save report
        report_dir = Path("outputs/reports/daily")
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"report_{start_date.date().isoformat()}.json"

        with open(report_path, "w") as f:
            json.dump(daily_report, f, indent=2)

        logger.info(f"Daily report generated: {report_path}")

        return {"report_path": str(report_path), "date": start_date.date().isoformat()}

    except Exception as e:
        logger.error(f"Failed to generate daily report: {e}")
        raise
    finally:
        session.close()


@celery_app.task(name="src.scheduler.automation.scheduled_video_generation")
def scheduled_video_generation(
    digital_human_id: int, text: str, mode: str = "enhanced_talking_head"
) -> Dict[str, Any]:
    """
    Generate video on schedule.

    Args:
        digital_human_id: Digital human ID
        text: Text to synthesize
        mode: Generation mode

    Returns:
        Dict with video path and metadata
    """
    import os

    database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/openuser")
    db_manager = DatabaseManager(database_url)
    session = db_manager.get_session()

    try:
        from src.scheduler.tasks import video_generation_task

        # Create task in database
        digital_human = (
            session.query(DigitalHuman).filter(DigitalHuman.id == digital_human_id).first()
        )
        if not digital_human:
            raise ValueError(f"Digital human {digital_human_id} not found")

        task = TaskModel(
            user_id=digital_human.user_id,
            name=f"Scheduled video generation - {digital_human.name}",
            task_type=TaskType.VIDEO_GENERATION,
            params={"digital_human_id": digital_human_id, "text": text, "mode": mode},
            status=TaskStatus.PENDING,
        )
        session.add(task)
        session.commit()

        # Queue video generation task
        result = video_generation_task.delay(
            task_id=task.id, digital_human_id=digital_human_id, text=text, mode=mode
        )

        logger.info(f"Scheduled video generation queued: task_id={task.id}")

        return {"task_id": task.id, "celery_task_id": result.id}

    except Exception as e:
        logger.error(f"Failed to schedule video generation: {e}")
        raise
    finally:
        session.close()


@celery_app.task(name="src.scheduler.automation.batch_processing")
def batch_processing(batch_type: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process batch of items.

    Args:
        batch_type: Type of batch processing (video_generation, voice_synthesis)
        items: List of items to process

    Returns:
        Dict with batch processing results
    """
    import os

    database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/openuser")
    db_manager = DatabaseManager(database_url)
    session = db_manager.get_session()

    try:
        processor = BatchProcessor(session)

        if batch_type == "video_generation":
            results = processor.process_video_generation_batch(items)
        elif batch_type == "voice_synthesis":
            results = processor.process_voice_synthesis_batch(items)
        else:
            raise ValueError(f"Unknown batch type: {batch_type}")

        logger.info(f"Batch processing completed: {batch_type}, {len(results)} items")

        return {"batch_type": batch_type, "total": len(items), "results": results}

    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise
    finally:
        session.close()


@celery_app.task(name="src.scheduler.automation.cleanup_maintenance")
def cleanup_maintenance() -> Dict[str, Any]:
    """
    Run cleanup and maintenance tasks.

    This task runs daily to:
    - Cleanup old tasks
    - Cleanup temporary files
    - Optimize database

    Returns:
        Dict with cleanup statistics
    """
    import os

    database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/openuser")
    db_manager = DatabaseManager(database_url)
    session = db_manager.get_session()

    try:
        cleanup_mgr = CleanupManager(session)

        # Cleanup old tasks
        task_cleanup = cleanup_mgr.cleanup_old_tasks(completed_days=30, failed_days=7)

        # Cleanup temp files
        file_cleanup = cleanup_mgr.cleanup_temp_files(temp_dir="outputs/temp", days=7)

        logger.info(f"Cleanup maintenance completed: {task_cleanup}, {file_cleanup}")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "task_cleanup": task_cleanup,
            "file_cleanup": file_cleanup,
        }

    except Exception as e:
        logger.error(f"Cleanup maintenance failed: {e}")
        raise
    finally:
        session.close()







