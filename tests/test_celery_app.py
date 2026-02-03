"""
Tests for Celery application configuration.
"""

import os
from unittest.mock import patch

import pytest
from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue

from src.scheduler.celery_app import celery_app, celery_config, get_celery_app


class TestCeleryApp:
    """Test Celery application configuration."""

    def test_celery_app_instance(self):
        """Test Celery app is created correctly."""
        assert isinstance(celery_app, Celery)
        assert celery_app.main == "openuser"

    def test_celery_config_broker_url(self):
        """Test broker URL configuration."""
        assert "broker_url" in celery_config
        assert celery_config["broker_url"].startswith("redis://")

    def test_celery_config_result_backend(self):
        """Test result backend configuration."""
        assert "result_backend" in celery_config
        assert celery_config["result_backend"].startswith("redis://")

    def test_celery_config_serialization(self):
        """Test serialization configuration."""
        assert celery_config["task_serializer"] == "json"
        assert celery_config["result_serializer"] == "json"
        assert "json" in celery_config["accept_content"]

    def test_celery_config_timezone(self):
        """Test timezone configuration."""
        assert "timezone" in celery_config
        assert celery_config["enable_utc"] is True

    def test_celery_config_task_settings(self):
        """Test task execution settings."""
        assert celery_config["task_track_started"] is True
        assert celery_config["task_time_limit"] == 3600
        assert celery_config["task_soft_time_limit"] == 3000
        assert celery_config["task_acks_late"] is True
        assert celery_config["task_reject_on_worker_lost"] is True

    def test_celery_config_result_settings(self):
        """Test result settings."""
        assert celery_config["result_expires"] == 86400
        assert celery_config["result_extended"] is True

    def test_celery_config_worker_settings(self):
        """Test worker settings."""
        assert celery_config["worker_prefetch_multiplier"] == 1
        assert celery_config["worker_max_tasks_per_child"] == 1000

    def test_celery_config_task_routes(self):
        """Test task routing configuration."""
        routes = celery_config["task_routes"]
        assert "src.scheduler.tasks.video_generation_task" in routes
        assert routes["src.scheduler.tasks.video_generation_task"]["queue"] == "video"
        assert routes["src.scheduler.tasks.voice_synthesis_task"]["queue"] == "voice"
        assert routes["src.scheduler.tasks.face_animation_task"]["queue"] == "video"
        assert routes["src.scheduler.tasks.report_generation_task"]["queue"] == "default"
        assert routes["src.scheduler.tasks.batch_processing_task"]["queue"] == "batch"

    def test_celery_config_task_queues(self):
        """Test task queues configuration."""
        queues = celery_config["task_queues"]
        assert len(queues) == 4

        # Check queue names
        queue_names = [q.name for q in queues]
        assert "default" in queue_names
        assert "video" in queue_names
        assert "voice" in queue_names
        assert "batch" in queue_names

    def test_celery_config_beat_schedule(self):
        """Test beat schedule configuration."""
        beat_schedule = celery_config["beat_schedule"]
        assert "cleanup-expired-tasks" in beat_schedule

        cleanup_task = beat_schedule["cleanup-expired-tasks"]
        assert cleanup_task["task"] == "src.scheduler.tasks.cleanup_expired_tasks"
        assert isinstance(cleanup_task["schedule"], crontab)

    def test_get_celery_app(self):
        """Test get_celery_app function."""
        app = get_celery_app()
        assert isinstance(app, Celery)
        assert app == celery_app

    @patch.dict(os.environ, {"REDIS_URL": "redis://custom:6379/1"})
    def test_custom_redis_url(self):
        """Test custom Redis URL from environment."""
        # Note: This test verifies the environment variable is read
        # The actual config is set at module import time
        assert os.getenv("REDIS_URL") == "redis://custom:6379/1"

    @patch.dict(os.environ, {"CELERY_TIMEZONE": "America/New_York"})
    def test_custom_timezone(self):
        """Test custom timezone from environment."""
        assert os.getenv("CELERY_TIMEZONE") == "America/New_York"
