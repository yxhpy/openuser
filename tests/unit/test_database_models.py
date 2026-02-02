"""Tests for database models"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from src.models.base import Base, DatabaseManager, TimestampMixin
from src.models.user import User
from src.models.digital_human import DigitalHuman
from src.models.task import Task, TaskStatus, TaskType


@pytest.fixture
def db_manager() -> DatabaseManager:
    """Create in-memory database for testing"""
    db = DatabaseManager("sqlite:///:memory:", echo=False)
    db.create_tables()
    return db


@pytest.fixture
def db_session(db_manager: DatabaseManager) -> Session:
    """Create database session"""
    session = db_manager.get_session()
    yield session
    session.close()


class TestDatabaseManager:
    """Test DatabaseManager class"""

    def test_create_tables(self) -> None:
        """Test table creation"""
        db = DatabaseManager("sqlite:///:memory:")
        db.create_tables()

        # Verify tables exist
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        assert "users" in tables
        assert "digital_humans" in tables
        assert "tasks" in tables

    def test_drop_tables(self) -> None:
        """Test table dropping"""
        db = DatabaseManager("sqlite:///:memory:")
        db.create_tables()
        db.drop_tables()

        # Verify tables don't exist
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        assert len(tables) == 0

    def test_get_session(self, db_manager: DatabaseManager) -> None:
        """Test session creation"""
        session = db_manager.get_session()
        assert isinstance(session, Session)
        session.close()


class TestUserModel:
    """Test User model"""

    def test_create_user(self, db_session: Session) -> None:
        """Test user creation"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_unique_username(self, db_session: Session) -> None:
        """Test username uniqueness constraint"""
        user1 = User(
            username="testuser",
            email="test1@example.com",
            password_hash="hash1",
        )
        user2 = User(
            username="testuser",
            email="test2@example.com",
            password_hash="hash2",
        )
        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_user_unique_email(self, db_session: Session) -> None:
        """Test email uniqueness constraint"""
        user1 = User(
            username="user1",
            email="test@example.com",
            password_hash="hash1",
        )
        user2 = User(
            username="user2",
            email="test@example.com",
            password_hash="hash2",
        )
        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()

    def test_user_repr(self, db_session: Session) -> None:
        """Test user string representation"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        assert "testuser" in repr(user)
        assert "test@example.com" in repr(user)


class TestDigitalHumanModel:
    """Test DigitalHuman model"""

    def test_create_digital_human(self, db_session: Session) -> None:
        """Test digital human creation"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        dh = DigitalHuman(
            user_id=user.id,
            name="Test Digital Human",
            description="A test digital human",
            image_path="/path/to/image.jpg",
            voice_model_path="/path/to/voice.pth",
        )
        db_session.add(dh)
        db_session.commit()

        assert dh.id is not None
        assert dh.user_id == user.id
        assert dh.name == "Test Digital Human"
        assert dh.description == "A test digital human"
        assert dh.is_active is True
        assert isinstance(dh.created_at, datetime)

    def test_digital_human_user_relationship(self, db_session: Session) -> None:
        """Test relationship between digital human and user"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        dh = DigitalHuman(
            user_id=user.id,
            name="Test DH",
        )
        db_session.add(dh)
        db_session.commit()

        # Test relationship
        assert dh.user == user
        assert dh in user.digital_humans

    def test_digital_human_cascade_delete(self, db_session: Session) -> None:
        """Test cascade delete when user is deleted"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        dh = DigitalHuman(user_id=user.id, name="Test DH")
        db_session.add(dh)
        db_session.commit()

        dh_id = dh.id

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Verify digital human is also deleted
        deleted_dh = db_session.get(DigitalHuman, dh_id)
        assert deleted_dh is None

    def test_digital_human_repr(self, db_session: Session) -> None:
        """Test digital human string representation"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        dh = DigitalHuman(user_id=user.id, name="Test DH")
        db_session.add(dh)
        db_session.commit()

        assert "Test DH" in repr(dh)
        assert str(user.id) in repr(dh)


class TestTaskModel:
    """Test Task model"""

    def test_create_task(self, db_session: Session) -> None:
        """Test task creation"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        task = Task(
            user_id=user.id,
            name="Test Task",
            description="A test task",
            task_type=TaskType.VIDEO_GENERATION.value,
            schedule="0 0 * * *",
            params={"key": "value"},
        )
        db_session.add(task)
        db_session.commit()

        assert task.id is not None
        assert task.user_id == user.id
        assert task.name == "Test Task"
        assert task.task_type == TaskType.VIDEO_GENERATION.value
        assert task.status == TaskStatus.PENDING.value
        assert task.params == {"key": "value"}
        assert isinstance(task.created_at, datetime)

    def test_task_user_relationship(self, db_session: Session) -> None:
        """Test relationship between task and user"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        task = Task(
            user_id=user.id,
            name="Test Task",
            task_type=TaskType.CUSTOM.value,
        )
        db_session.add(task)
        db_session.commit()

        # Test relationship
        assert task.user == user
        assert task in user.tasks

    def test_task_cascade_delete(self, db_session: Session) -> None:
        """Test cascade delete when user is deleted"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        task = Task(
            user_id=user.id,
            name="Test Task",
            task_type=TaskType.CUSTOM.value,
        )
        db_session.add(task)
        db_session.commit()

        task_id = task.id

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Verify task is also deleted
        deleted_task = db_session.get(Task, task_id)
        assert deleted_task is None

    def test_task_status_enum(self, db_session: Session) -> None:
        """Test task status enumeration"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_task_type_enum(self, db_session: Session) -> None:
        """Test task type enumeration"""
        assert TaskType.VIDEO_GENERATION.value == "video_generation"
        assert TaskType.VOICE_SYNTHESIS.value == "voice_synthesis"
        assert TaskType.FACE_ANIMATION.value == "face_animation"
        assert TaskType.REPORT_GENERATION.value == "report_generation"
        assert TaskType.BATCH_PROCESSING.value == "batch_processing"
        assert TaskType.CUSTOM.value == "custom"

    def test_task_repr(self, db_session: Session) -> None:
        """Test task string representation"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        task = Task(
            user_id=user.id,
            name="Test Task",
            task_type=TaskType.CUSTOM.value,
        )
        db_session.add(task)
        db_session.commit()

        assert "Test Task" in repr(task)
        assert TaskStatus.PENDING.value in repr(task)
