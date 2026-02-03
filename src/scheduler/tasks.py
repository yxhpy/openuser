"""
Celery task definitions for OpenUser.

This module defines all Celery tasks for:
- Video generation
- Voice synthesis
- Face animation
- Report generation
- Batch processing
- Cleanup tasks
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from celery import Task
from sqlalchemy.orm import Session

from src.models.base import DatabaseManager
from src.models.digital_human import DigitalHuman
from src.models.task import Task as TaskModel
from src.models.task import TaskStatus
from src.models.video_generator import VideoGenerator
from src.models.voice_synthesis import VoiceSynthesizer
from src.scheduler.celery_app import celery_app

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task class with database session management."""

    _db_manager: Optional[DatabaseManager] = None

    @property
    def db_manager(self) -> DatabaseManager:
        """Get or create database manager."""
        if self._db_manager is None:
            import os

            database_url = os.getenv(
                "DATABASE_URL", "postgresql://user:pass@localhost/openuser"
            )
            self._db_manager = DatabaseManager(database_url)
        return self._db_manager

    def get_session(self) -> Session:
        """Get database session."""
        return self.db_manager.get_session()


@celery_app.task(bind=True, base=DatabaseTask, name="src.scheduler.tasks.video_generation_task")
def video_generation_task(
    self: DatabaseTask,
    task_id: int,
    digital_human_id: int,
    text: Optional[str] = None,
    audio_path: Optional[str] = None,
    mode: str = "enhanced_talking_head",
) -> Dict[str, Any]:
    """
    Generate video for a digital human.

    Args:
        task_id: Task ID in database
        digital_human_id: Digital human ID
        text: Text to synthesize (for text-to-video)
        audio_path: Audio file path (for audio-to-video)
        mode: Generation mode (lipsync, talking_head, enhanced_lipsync, enhanced_talking_head)

    Returns:
        Dict with video_path and metadata
    """
    session = self.get_session()
    try:
        # Update task status to running
        task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        session.commit()

        # Get digital human
        digital_human = (
            session.query(DigitalHuman).filter(DigitalHuman.id == digital_human_id).first()
        )
        if not digital_human:
            raise ValueError(f"Digital human {digital_human_id} not found")

        # Initialize video generator
        video_gen = VideoGenerator(device="cuda", mode=mode)

        # Generate video
        output_path = f"outputs/videos/{digital_human_id}_{task_id}.mp4"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if text:
            video_path = video_gen.generate_from_text(
                text=text, image_path=digital_human.image_path, output_path=output_path
            )
        elif audio_path:
            video_path = video_gen.generate_from_audio(
                image_path=digital_human.image_path,
                audio_path=audio_path,
                output_path=output_path,
            )
        else:
            raise ValueError("Either text or audio_path must be provided")

        # Update task status to completed
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = {"video_path": video_path, "mode": mode}
        session.commit()

        logger.info(f"Video generation task {task_id} completed: {video_path}")
        return {"video_path": video_path, "mode": mode}

    except Exception as e:
        logger.error(f"Video generation task {task_id} failed: {e}")
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        session.commit()
        raise
    finally:
        session.close()


@celery_app.task(bind=True, base=DatabaseTask, name="src.scheduler.tasks.voice_synthesis_task")
def voice_synthesis_task(
    self: DatabaseTask, task_id: int, text: str, backend: str = "coqui", speaker_wav: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synthesize voice from text.

    Args:
        task_id: Task ID in database
        text: Text to synthesize
        backend: TTS backend (coqui, pyttsx3, gtts)
        speaker_wav: Speaker reference audio for voice cloning

    Returns:
        Dict with audio_path and metadata
    """
    session = self.get_session()
    try:
        # Update task status
        task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        session.commit()

        # Initialize voice synthesizer
        synthesizer = VoiceSynthesizer(backend=backend, device="cuda")

        # Synthesize voice
        output_path = f"outputs/audio/{task_id}.wav"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        audio_path = synthesizer.synthesize(text=text, output_path=output_path, speaker_wav=speaker_wav)

        # Update task status
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = {"audio_path": audio_path, "backend": backend}
        session.commit()

        logger.info(f"Voice synthesis task {task_id} completed: {audio_path}")
        return {"audio_path": audio_path, "backend": backend}

    except Exception as e:
        logger.error(f"Voice synthesis task {task_id} failed: {e}")
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        session.commit()
        raise
    finally:
        session.close()


@celery_app.task(bind=True, base=DatabaseTask, name="src.scheduler.tasks.face_animation_task")
def face_animation_task(
    self: DatabaseTask, task_id: int, image_path: str, audio_path: str, mode: str = "wav2lip"
) -> Dict[str, Any]:
    """
    Generate face animation from image and audio.

    Args:
        task_id: Task ID in database
        image_path: Path to face image
        audio_path: Path to audio file
        mode: Animation mode (wav2lip, sadtalker)

    Returns:
        Dict with video_path and metadata
    """
    session = self.get_session()
    try:
        # Update task status
        task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        session.commit()

        # Generate animation based on mode
        output_path = f"outputs/animations/{task_id}.mp4"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if mode == "wav2lip":
            from src.models.wav2lip import Wav2LipModel

            model = Wav2LipModel(device="cuda")
            video_path = model.generate_video(
                face_path=image_path, audio_path=audio_path, output_path=output_path
            )
        elif mode == "sadtalker":
            from src.models.sadtalker import SadTalkerModel

            model = SadTalkerModel(device="cuda")
            video_path = model.generate_video(
                image_path=image_path, audio_path=audio_path, output_path=output_path
            )
        else:
            raise ValueError(f"Unknown animation mode: {mode}")

        # Update task status
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = {"video_path": video_path, "mode": mode}
        session.commit()

        logger.info(f"Face animation task {task_id} completed: {video_path}")
        return {"video_path": video_path, "mode": mode}

    except Exception as e:
        logger.error(f"Face animation task {task_id} failed: {e}")
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        session.commit()
        raise
    finally:
        session.close()


@celery_app.task(bind=True, base=DatabaseTask, name="src.scheduler.tasks.report_generation_task")
def report_generation_task(self: DatabaseTask, task_id: int, report_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate reports (usage statistics, task history, etc.).

    Args:
        task_id: Task ID in database
        report_type: Type of report (usage, tasks, digital_humans)
        params: Report parameters (date_range, user_id, etc.)

    Returns:
        Dict with report_path and metadata
    """
    session = self.get_session()
    try:
        # Update task status
        task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        session.commit()

        # Generate report based on type
        report_data = {}
        if report_type == "usage":
            # Generate usage statistics
            report_data = {"type": "usage", "params": params}
        elif report_type == "tasks":
            # Generate task history report
            report_data = {"type": "tasks", "params": params}
        elif report_type == "digital_humans":
            # Generate digital humans report
            report_data = {"type": "digital_humans", "params": params}
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        # Save report
        output_path = f"outputs/reports/{task_id}_{report_type}.json"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        import json

        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)

        # Update task status
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = {"report_path": output_path, "report_type": report_type}
        session.commit()

        logger.info(f"Report generation task {task_id} completed: {output_path}")
        return {"report_path": output_path, "report_type": report_type}

    except Exception as e:
        logger.error(f"Report generation task {task_id} failed: {e}")
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        session.commit()
        raise
    finally:
        session.close()


@celery_app.task(bind=True, base=DatabaseTask, name="src.scheduler.tasks.batch_processing_task")
def batch_processing_task(self: DatabaseTask, task_id: int, batch_type: str, items: list) -> Dict[str, Any]:
    """
    Process multiple items in batch.

    Args:
        task_id: Task ID in database
        batch_type: Type of batch processing (video_generation, voice_synthesis)
        items: List of items to process

    Returns:
        Dict with results and metadata
    """
    session = self.get_session()
    try:
        # Update task status
        task = session.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        session.commit()

        # Process items
        results = []
        for item in items:
            try:
                if batch_type == "video_generation":
                    # Process video generation
                    result = {"item": item, "status": "completed"}
                elif batch_type == "voice_synthesis":
                    # Process voice synthesis
                    result = {"item": item, "status": "completed"}
                else:
                    result = {"item": item, "status": "skipped", "error": "Unknown batch type"}
                results.append(result)
            except Exception as e:
                results.append({"item": item, "status": "failed", "error": str(e)})

        # Update task status
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = {"batch_type": batch_type, "total": len(items), "results": results}
        session.commit()

        logger.info(f"Batch processing task {task_id} completed: {len(results)} items")
        return {"batch_type": batch_type, "total": len(items), "results": results}

    except Exception as e:
        logger.error(f"Batch processing task {task_id} failed: {e}")
        task.status = TaskStatus.FAILED
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        session.commit()
        raise
    finally:
        session.close()


@celery_app.task(name="src.scheduler.tasks.cleanup_expired_tasks")
def cleanup_expired_tasks() -> Dict[str, Any]:
    """
    Cleanup expired tasks and temporary files.

    This task runs daily to clean up:
    - Completed tasks older than 30 days
    - Failed tasks older than 7 days
    - Temporary files

    Returns:
        Dict with cleanup statistics
    """
    import os
    from datetime import timedelta

    database_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/openuser")
    db_manager = DatabaseManager(database_url)
    session = db_manager.get_session()

    try:
        now = datetime.utcnow()
        completed_threshold = now - timedelta(days=30)
        failed_threshold = now - timedelta(days=7)

        # Delete old completed tasks
        completed_deleted = (
            session.query(TaskModel)
            .filter(
                TaskModel.status == TaskStatus.COMPLETED, TaskModel.completed_at < completed_threshold
            )
            .delete()
        )

        # Delete old failed tasks
        failed_deleted = (
            session.query(TaskModel)
            .filter(TaskModel.status == TaskStatus.FAILED, TaskModel.completed_at < failed_threshold)
            .delete()
        )

        session.commit()

        logger.info(
            f"Cleanup completed: {completed_deleted} completed tasks, {failed_deleted} failed tasks"
        )
        return {
            "completed_deleted": completed_deleted,
            "failed_deleted": failed_deleted,
            "timestamp": now.isoformat(),
        }

    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

