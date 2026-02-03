"""
Scheduler module for task automation and scheduling.

This module provides Celery-based task scheduling with:
- Cron-based scheduling
- Task queue management
- Task monitoring and logging
- Integration with digital human pipeline
"""

from src.scheduler.celery_app import celery_app, get_celery_app
from src.scheduler.monitor import TaskMonitor, get_task_monitor
from src.scheduler.schedule_manager import ScheduleManager, get_schedule_manager
from src.scheduler.tasks import (
    batch_processing_task,
    cleanup_expired_tasks,
    face_animation_task,
    report_generation_task,
    video_generation_task,
    voice_synthesis_task,
)

__all__ = [
    "celery_app",
    "get_celery_app",
    "video_generation_task",
    "voice_synthesis_task",
    "face_animation_task",
    "report_generation_task",
    "batch_processing_task",
    "cleanup_expired_tasks",
    "ScheduleManager",
    "get_schedule_manager",
    "TaskMonitor",
    "get_task_monitor",
]
