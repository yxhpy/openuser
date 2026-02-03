"""
Task monitoring and logging system.

This module provides:
- Task execution monitoring
- Task statistics and metrics
- Real-time progress tracking
- Task history and logging
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.base import DatabaseManager
from src.models.task import Task as TaskModel
from src.models.task import TaskStatus, TaskType

logger = logging.getLogger(__name__)


class TaskMonitor:
    """Monitor for task execution and statistics."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize task monitor.

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager

    def get_task_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get task statistics.

        Args:
            user_id: Filter by user ID (optional)

        Returns:
            Dict with task statistics
        """
        session = self.db_manager.get_session()
        try:
            query = session.query(TaskModel)
            if user_id is not None:
                query = query.filter(TaskModel.user_id == user_id)

            # Count by status
            total = query.count()
            pending = query.filter(TaskModel.status == TaskStatus.PENDING).count()
            running = query.filter(TaskModel.status == TaskStatus.RUNNING).count()
            completed = query.filter(TaskModel.status == TaskStatus.COMPLETED).count()
            failed = query.filter(TaskModel.status == TaskStatus.FAILED).count()
            cancelled = query.filter(TaskModel.status == TaskStatus.CANCELLED).count()

            # Count by type
            by_type = {}
            for task_type in TaskType:
                count = query.filter(TaskModel.task_type == task_type).count()
                by_type[task_type.value] = count

            # Calculate success rate
            success_rate = (completed / total * 100) if total > 0 else 0.0

            return {
                "total": total,
                "by_status": {
                    "pending": pending,
                    "running": running,
                    "completed": completed,
                    "failed": failed,
                    "cancelled": cancelled,
                },
                "by_type": by_type,
                "success_rate": round(success_rate, 2),
            }

        finally:
            session.close()

    def get_task_history(
        self,
        user_id: Optional[int] = None,
        task_type: Optional[TaskType] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get task execution history.

        Args:
            user_id: Filter by user ID
            task_type: Filter by task type
            status: Filter by status
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of task history records
        """
        session = self.db_manager.get_session()
        try:
            query = session.query(TaskModel)

            if user_id is not None:
                query = query.filter(TaskModel.user_id == user_id)

            if task_type is not None:
                query = query.filter(TaskModel.task_type == task_type)

            if status is not None:
                query = query.filter(TaskModel.status == status)

            # Order by created_at descending
            query = query.order_by(TaskModel.created_at.desc())

            # Apply pagination
            tasks = query.limit(limit).offset(offset).all()

            # Convert to dict
            history = []
            for task in tasks:
                history.append(
                    {
                        "id": task.id,
                        "name": task.name,
                        "task_type": task.task_type.value,
                        "status": task.status.value,
                        "created_at": task.created_at.isoformat() if task.created_at else None,
                        "started_at": task.started_at.isoformat() if task.started_at else None,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "duration": self._calculate_duration(task),
                        "error_message": task.error_message,
                    }
                )

            return history

        finally:
            session.close()

    def get_recent_failures(
        self, user_id: Optional[int] = None, hours: int = 24, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent failed tasks.

        Args:
            user_id: Filter by user ID
            hours: Look back hours
            limit: Maximum number of results

        Returns:
            List of failed task records
        """
        session = self.db_manager.get_session()
        try:
            threshold = datetime.utcnow() - timedelta(hours=hours)

            query = (
                session.query(TaskModel)
                .filter(TaskModel.status == TaskStatus.FAILED)
                .filter(TaskModel.completed_at >= threshold)
            )

            if user_id is not None:
                query = query.filter(TaskModel.user_id == user_id)

            tasks = query.order_by(TaskModel.completed_at.desc()).limit(limit).all()

            failures = []
            for task in tasks:
                failures.append(
                    {
                        "id": task.id,
                        "name": task.name,
                        "task_type": task.task_type.value,
                        "error_message": task.error_message,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    }
                )

            return failures

        finally:
            session.close()

    def get_performance_metrics(
        self, user_id: Optional[int] = None, days: int = 7
    ) -> Dict[str, Any]:
        """
        Get performance metrics for the last N days.

        Args:
            user_id: Filter by user ID
            days: Number of days to analyze

        Returns:
            Dict with performance metrics
        """
        session = self.db_manager.get_session()
        try:
            threshold = datetime.utcnow() - timedelta(days=days)

            query = session.query(TaskModel).filter(TaskModel.created_at >= threshold)

            if user_id is not None:
                query = query.filter(TaskModel.user_id == user_id)

            tasks = query.all()

            if not tasks:
                return {
                    "total_tasks": 0,
                    "avg_duration_seconds": 0,
                    "success_rate": 0,
                    "tasks_per_day": 0,
                }

            # Calculate metrics
            completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
            durations = [self._calculate_duration(t) for t in completed_tasks if self._calculate_duration(t)]

            avg_duration = sum(durations) / len(durations) if durations else 0
            success_rate = (len(completed_tasks) / len(tasks) * 100) if tasks else 0
            tasks_per_day = len(tasks) / days

            return {
                "total_tasks": len(tasks),
                "avg_duration_seconds": round(avg_duration, 2),
                "success_rate": round(success_rate, 2),
                "tasks_per_day": round(tasks_per_day, 2),
            }

        finally:
            session.close()

    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status.

        Returns:
            Dict with queue statistics
        """
        session = self.db_manager.get_session()
        try:
            # Count pending and running tasks
            pending = session.query(TaskModel).filter(TaskModel.status == TaskStatus.PENDING).count()
            running = session.query(TaskModel).filter(TaskModel.status == TaskStatus.RUNNING).count()

            # Count by type for pending tasks
            pending_by_type = {}
            for task_type in TaskType:
                count = (
                    session.query(TaskModel)
                    .filter(TaskModel.status == TaskStatus.PENDING)
                    .filter(TaskModel.task_type == task_type)
                    .count()
                )
                pending_by_type[task_type.value] = count

            return {
                "pending": pending,
                "running": running,
                "pending_by_type": pending_by_type,
            }

        finally:
            session.close()

    def _calculate_duration(self, task: TaskModel) -> Optional[float]:
        """
        Calculate task duration in seconds.

        Args:
            task: Task model

        Returns:
            Duration in seconds or None
        """
        if task.started_at and task.completed_at:
            delta = task.completed_at - task.started_at
            return delta.total_seconds()
        return None


def get_task_monitor() -> TaskMonitor:
    """Get task monitor instance."""
    import os

    database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/openuser")
    db_manager = DatabaseManager(database_url)
    return TaskMonitor(db_manager)
