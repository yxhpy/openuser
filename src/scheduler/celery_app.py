"""
Celery application configuration.

This module configures the Celery application with:
- Redis broker and result backend
- Task routing and queues
- Worker settings
- Timezone configuration
- Task serialization
"""

import os
from typing import Any, Dict

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

# Get configuration from environment variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "UTC")

# Create Celery application
celery_app = Celery("openuser")

# Celery configuration
celery_config: Dict[str, Any] = {
    # Broker settings
    "broker_url": CELERY_BROKER_URL,
    "result_backend": CELERY_RESULT_BACKEND,
    "broker_connection_retry_on_startup": True,
    # Task settings
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],
    "timezone": CELERY_TIMEZONE,
    "enable_utc": True,
    # Task execution settings
    "task_track_started": True,
    "task_time_limit": 3600,  # 1 hour hard limit
    "task_soft_time_limit": 3000,  # 50 minutes soft limit
    "task_acks_late": True,
    "task_reject_on_worker_lost": True,
    # Result settings
    "result_expires": 86400,  # Results expire after 24 hours
    "result_extended": True,
    # Worker settings
    "worker_prefetch_multiplier": 1,
    "worker_max_tasks_per_child": 1000,
    # Task routing
    "task_routes": {
        "src.scheduler.tasks.video_generation_task": {"queue": "video"},
        "src.scheduler.tasks.voice_synthesis_task": {"queue": "voice"},
        "src.scheduler.tasks.face_animation_task": {"queue": "video"},
        "src.scheduler.tasks.report_generation_task": {"queue": "default"},
        "src.scheduler.tasks.batch_processing_task": {"queue": "batch"},
    },
    # Task queues
    "task_queues": (
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("video", Exchange("video"), routing_key="video", priority=5),
        Queue("voice", Exchange("voice"), routing_key="voice", priority=3),
        Queue("batch", Exchange("batch"), routing_key="batch", priority=1),
    ),
    # Beat schedule (cron-based scheduling)
    "beat_schedule": {
        # Example: cleanup expired tasks every day at 2 AM
        "cleanup-expired-tasks": {
            "task": "src.scheduler.tasks.cleanup_expired_tasks",
            "schedule": crontab(hour=2, minute=0),
        },
    },
}

# Apply configuration
celery_app.config_from_object(celery_config)

# Auto-discover tasks from all modules
celery_app.autodiscover_tasks(["src.scheduler"])


def get_celery_app() -> Celery:
    """Get the Celery application instance."""
    return celery_app

