"""
Schedule manager for dynamic task scheduling.

This module provides dynamic scheduling capabilities:
- Create/update/delete scheduled tasks
- Cron expression parsing and validation
- Integration with Celery Beat
- Persistent schedule storage
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from celery import Celery
from celery.schedules import crontab, schedule
from sqlalchemy.orm import Session

from src.models.base import DatabaseManager
from src.models.task import Task as TaskModel
from src.models.task import TaskStatus, TaskType
from src.scheduler.celery_app import celery_app

logger = logging.getLogger(__name__)


class ScheduleManager:
    """Manager for dynamic task scheduling."""

    def __init__(self, celery_app: Celery, db_manager: DatabaseManager):
        """
        Initialize schedule manager.

        Args:
            celery_app: Celery application instance
            db_manager: Database manager instance
        """
        self.celery_app = celery_app
        self.db_manager = db_manager

    def create_schedule(
        self,
        user_id: int,
        name: str,
        task_type: TaskType,
        schedule_expr: str,
        params: Dict[str, Any],
        description: Optional[str] = None,
    ) -> TaskModel:
        """
        Create a new scheduled task.

        Args:
            user_id: User ID
            name: Task name
            task_type: Task type
            schedule_expr: Cron expression (e.g., "0 2 * * *")
            params: Task parameters
            description: Task description

        Returns:
            Created task model

        Raises:
            ValueError: If schedule expression is invalid
        """
        # Validate cron expression
        if not self.validate_cron_expression(schedule_expr):
            raise ValueError(f"Invalid cron expression: {schedule_expr}")

        session = self.db_manager.get_session()
        try:
            # Create task in database
            task = TaskModel(
                user_id=user_id,
                name=name,
                description=description,
                task_type=task_type,
                schedule=schedule_expr,
                params=params,
                status=TaskStatus.PENDING,
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            # Register with Celery Beat
            self._register_beat_schedule(task)

            logger.info(f"Created scheduled task: {name} (ID: {task.id})")
            return task

        finally:
            session.close()

    def update_schedule(
        self,
        task_id: int,
        schedule_expr: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> TaskModel:
        """
        Update an existing scheduled task.

        Args:
            task_id: Task ID
            schedule_expr: New cron expression
            params: New task parameters
            name: New task name
            description: New task description

        Returns:
            Updated task model

        Raises:
            ValueError: If task not found or schedule expression is invalid
        """
        session = self.db_manager.get_session()
        try:
            task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if not task:
                raise ValueError(f"Task {task_id} not found")

            # Update fields
            if schedule_expr is not None:
                if not self.validate_cron_expression(schedule_expr):
                    raise ValueError(f"Invalid cron expression: {schedule_expr}")
                task.schedule = schedule_expr

            if params is not None:
                task.params = params

            if name is not None:
                task.name = name

            if description is not None:
                task.description = description

            session.commit()
            session.refresh(task)

            # Update Celery Beat schedule
            self._register_beat_schedule(task)

            logger.info(f"Updated scheduled task: {task.name} (ID: {task.id})")
            return task

        finally:
            session.close()

    def delete_schedule(self, task_id: int) -> bool:
        """
        Delete a scheduled task.

        Args:
            task_id: Task ID

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If task not found
        """
        session = self.db_manager.get_session()
        try:
            task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
            if not task:
                raise ValueError(f"Task {task_id} not found")

            # Unregister from Celery Beat
            self._unregister_beat_schedule(task)

            # Delete from database
            session.delete(task)
            session.commit()

            logger.info(f"Deleted scheduled task: {task.name} (ID: {task.id})")
            return True

        finally:
            session.close()

    def get_schedule(self, task_id: int) -> Optional[TaskModel]:
        """
        Get a scheduled task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task model or None if not found
        """
        session = self.db_manager.get_session()
        try:
            return session.query(TaskModel).filter(TaskModel.id == task_id).first()
        finally:
            session.close()

    def list_schedules(
        self, user_id: Optional[int] = None, status: Optional[TaskStatus] = None
    ) -> List[TaskModel]:
        """
        List scheduled tasks.

        Args:
            user_id: Filter by user ID
            status: Filter by status

        Returns:
            List of task models
        """
        session = self.db_manager.get_session()
        try:
            query = session.query(TaskModel).filter(TaskModel.schedule.isnot(None))

            if user_id is not None:
                query = query.filter(TaskModel.user_id == user_id)

            if status is not None:
                query = query.filter(TaskModel.status == status)

            return query.all()

        finally:
            session.close()

    def validate_cron_expression(self, expr: str) -> bool:
        """
        Validate a cron expression.

        Args:
            expr: Cron expression (e.g., "0 2 * * *")

        Returns:
            True if valid, False otherwise
        """
        try:
            parts = expr.split()
            if len(parts) != 5:
                return False

            # Parse cron expression
            minute, hour, day_of_month, month, day_of_week = parts

            # Validate ranges
            self._validate_cron_field(minute, 0, 59)
            self._validate_cron_field(hour, 0, 23)
            self._validate_cron_field(day_of_month, 1, 31)
            self._validate_cron_field(month, 1, 12)
            self._validate_cron_field(day_of_week, 0, 6)

            return True

        except Exception:
            return False

    def _validate_cron_field(self, field: str, min_val: int, max_val: int) -> None:
        """
        Validate a single cron field.

        Args:
            field: Cron field value
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Raises:
            ValueError: If field is invalid
        """
        if field == "*":
            return

        # Handle ranges (e.g., "1-5")
        if "-" in field:
            start, end = field.split("-")
            start_val = int(start)
            end_val = int(end)
            if not (min_val <= start_val <= max_val and min_val <= end_val <= max_val):
                raise ValueError(f"Invalid range: {field}")
            return

        # Handle steps (e.g., "*/5")
        if "/" in field:
            base, step = field.split("/")
            if base != "*":
                base_val = int(base)
                if not (min_val <= base_val <= max_val):
                    raise ValueError(f"Invalid base: {base}")
            step_val = int(step)
            if step_val <= 0:
                raise ValueError(f"Invalid step: {step}")
            return

        # Handle lists (e.g., "1,3,5")
        if "," in field:
            for val in field.split(","):
                val_int = int(val)
                if not (min_val <= val_int <= max_val):
                    raise ValueError(f"Invalid value: {val}")
            return

        # Handle single value
        val = int(field)
        if not (min_val <= val <= max_val):
            raise ValueError(f"Invalid value: {field}")

    def _register_beat_schedule(self, task: TaskModel) -> None:
        """
        Register task with Celery Beat.

        Args:
            task: Task model
        """
        if not task.schedule:
            return

        # Parse cron expression
        parts = task.schedule.split()
        minute, hour, day_of_month, month, day_of_week = parts

        # Create crontab schedule
        schedule_obj = crontab(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month_of_year=month,
            day_of_week=day_of_week,
        )

        # Map task type to Celery task
        task_map = {
            TaskType.VIDEO_GENERATION: "src.scheduler.tasks.video_generation_task",
            TaskType.VOICE_SYNTHESIS: "src.scheduler.tasks.voice_synthesis_task",
            TaskType.FACE_ANIMATION: "src.scheduler.tasks.face_animation_task",
            TaskType.REPORT_GENERATION: "src.scheduler.tasks.report_generation_task",
            TaskType.BATCH_PROCESSING: "src.scheduler.tasks.batch_processing_task",
        }

        celery_task = task_map.get(task.task_type)
        if not celery_task:
            logger.warning(f"Unknown task type: {task.task_type}")
            return

        # Register with Celery Beat
        schedule_name = f"scheduled_task_{task.id}"
        self.celery_app.conf.beat_schedule[schedule_name] = {
            "task": celery_task,
            "schedule": schedule_obj,
            "args": (task.id,) + tuple(task.params.values()) if task.params else (task.id,),
        }

        logger.info(f"Registered beat schedule: {schedule_name}")

    def _unregister_beat_schedule(self, task: TaskModel) -> None:
        """
        Unregister task from Celery Beat.

        Args:
            task: Task model
        """
        schedule_name = f"scheduled_task_{task.id}"
        if schedule_name in self.celery_app.conf.beat_schedule:
            del self.celery_app.conf.beat_schedule[schedule_name]
            logger.info(f"Unregistered beat schedule: {schedule_name}")


def get_schedule_manager() -> ScheduleManager:
    """Get schedule manager instance."""
    import os

    database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/openuser")
    db_manager = DatabaseManager(database_url)
    return ScheduleManager(celery_app, db_manager)

