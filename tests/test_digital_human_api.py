"""
Tests for Digital Human API endpoints.
"""
import pytest
from pathlib import Path
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import create_app
from src.models.base import Base
from src.models.user import User
from src.models.digital_human import DigitalHuman
from src.models.task import Task
from src.models.video_generator import VideoGenerator
from src.api.digital_human import get_db_session, get_video_generator
from src.api.auth import get_db, get_current_user
from src.api.auth_utils import create_access_token


@pytest.fixture(scope="module")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool  # Use StaticPool to share connection across threads
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def test_db(test_engine):
    """Create test database session factory."""
    TestingSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    return TestingSessionLocal


@pytest.fixture(scope="module")
def test_user(test_engine):
    """Create test user."""
    TestingSessionLocal = sessionmaker(bind=test_engine)
    session = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True,
        is_superuser=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user
    session.close()


@pytest.fixture(scope="module")
def auth_token(test_user):
    """Create authentication token."""
    return create_access_token({"sub": test_user.username, "user_id": test_user.id})


@pytest.fixture
def client(test_db, test_user, auth_token):
    """Create test client with overridden dependencies."""
    app = create_app()

    def override_get_db():
        session = test_db()
        try:
            yield session
        finally:
            session.close()

    def override_get_current_user():
        return test_user

    def override_get_video_generator():
        mock_gen = Mock()
        mock_gen.generate_from_text = Mock(return_value="/fake/video.mp4")
        mock_gen.generate_from_audio = Mock(return_value="/fake/video.mp4")
        mock_gen.mode = None
        return mock_gen

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_video_generator] = override_get_video_generator

    return TestClient(app)


@pytest.fixture
def test_digital_human(test_engine, test_user):
    """Create test digital human."""
    TestingSessionLocal = sessionmaker(bind=test_engine)
    session = TestingSessionLocal()
    dh = DigitalHuman(
        user_id=test_user.id,
        name="Test Human",
        description="Test description",
        image_path="/fake/image.jpg",
        voice_model_path="/fake/voice.wav",
        is_active=True
    )
    session.add(dh)
    session.commit()
    session.refresh(dh)
    yield dh
    # Clean up after test
    session.delete(dh)
    session.commit()
    session.close()


def test_create_digital_human(client, auth_token, tmp_path):
    """Test creating a digital human."""
    # Create fake image file
    image_data = b"fake image data"
    image_file = BytesIO(image_data)
    image_file.name = "test.jpg"

    with patch("builtins.open", create=True) as mock_open:
        with patch("pathlib.Path.mkdir"):
            response = client.post(
                "/api/v1/digital-human/create",
                headers={"Authorization": f"Bearer {auth_token}"},
                data={
                    "name": "Test Human",
                    "description": "Test description",
                    "voice_model_path": "/fake/voice.wav"
                },
                files={"image": ("test.jpg", image_file, "image/jpeg")}
            )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Human"
    assert data["description"] == "Test description"
    assert data["is_active"] is True


def test_create_digital_human_invalid_file(client, auth_token):
    """Test creating digital human with invalid file type."""
    text_file = BytesIO(b"not an image")
    text_file.name = "test.txt"

    response = client.post(
        "/api/v1/digital-human/create",
        headers={"Authorization": f"Bearer {auth_token}"},
        data={"name": "Test Human"},
        files={"image": ("test.txt", text_file, "text/plain")}
    )

    assert response.status_code == 400
    assert "must be an image" in response.json()["detail"]


def test_create_digital_human_unauthorized(test_db):
    """Test creating digital human without authentication."""
    # Create a client without auth override
    app = create_app()

    def override_get_db():
        session = test_db()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_db_session] = override_get_db

    client = TestClient(app)

    image_file = BytesIO(b"fake image")
    image_file.name = "test.jpg"

    response = client.post(
        "/api/v1/digital-human/create",
        data={"name": "Test Human"},
        files={"image": ("test.jpg", image_file, "image/jpeg")}
    )

    assert response.status_code == 401


def test_generate_video_from_text(client, auth_token, test_digital_human):
    """Test generating video from text."""
    response = client.post(
        "/api/v1/digital-human/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        data={
            "digital_human_id": test_digital_human.id,
            "text": "Hello world",
            "mode": "enhanced_talking_head"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "video_path" in data
    assert data["digital_human_id"] == test_digital_human.id
    assert data["mode"] == "enhanced_talking_head"


def test_generate_video_from_audio(client, auth_token, test_digital_human):
    """Test generating video from audio."""
    audio_file = BytesIO(b"fake audio data")
    audio_file.name = "test.wav"

    with patch("builtins.open", create=True):
        with patch("pathlib.Path.mkdir"):
            response = client.post(
                "/api/v1/digital-human/generate",
                headers={"Authorization": f"Bearer {auth_token}"},
                data={
                    "digital_human_id": test_digital_human.id,
                    "mode": "lipsync"
                },
                files={"audio": ("test.wav", audio_file, "audio/wav")}
            )

    assert response.status_code == 200
    data = response.json()
    assert "video_path" in data
    assert data["mode"] == "lipsync"


def test_generate_video_no_input(client, auth_token, test_digital_human):
    """Test generating video without text or audio."""
    response = client.post(
        "/api/v1/digital-human/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        data={
            "digital_human_id": test_digital_human.id,
            "mode": "lipsync"
        }
    )

    assert response.status_code == 400
    assert "Either text or audio must be provided" in response.json()["detail"]


def test_generate_video_both_inputs(client, auth_token, test_digital_human):
    """Test generating video with both text and audio."""
    audio_file = BytesIO(b"fake audio")
    audio_file.name = "test.wav"

    response = client.post(
        "/api/v1/digital-human/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        data={
            "digital_human_id": test_digital_human.id,
            "text": "Hello",
            "mode": "lipsync"
        },
        files={"audio": ("test.wav", audio_file, "audio/wav")}
    )

    assert response.status_code == 400
    assert "Provide either text or audio, not both" in response.json()["detail"]


def test_generate_video_invalid_mode(client, auth_token, test_digital_human):
    """Test generating video with invalid mode."""
    response = client.post(
        "/api/v1/digital-human/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        data={
            "digital_human_id": test_digital_human.id,
            "text": "Hello",
            "mode": "invalid_mode"
        }
    )

    assert response.status_code == 400
    assert "Invalid mode" in response.json()["detail"]


def test_generate_video_not_found(client, auth_token):
    """Test generating video for non-existent digital human."""
    response = client.post(
        "/api/v1/digital-human/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        data={
            "digital_human_id": 99999,
            "text": "Hello",
            "mode": "lipsync"
        }
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_list_digital_humans(client, auth_token, test_digital_human):
    """Test listing digital humans."""
    response = client.get(
        "/api/v1/digital-human/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "digital_humans" in data
    assert "total" in data
    assert data["total"] >= 1
    assert any(dh["id"] == test_digital_human.id for dh in data["digital_humans"])


def test_list_digital_humans_empty(client, auth_token, test_engine):
    """Test listing digital humans when none exist."""
    # Clean up all digital humans first
    TestingSessionLocal = sessionmaker(bind=test_engine)
    session = TestingSessionLocal()
    session.query(DigitalHuman).delete()
    session.commit()
    session.close()

    response = client.get(
        "/api/v1/digital-human/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["digital_humans"]) == 0


def test_get_digital_human(client, auth_token, test_digital_human):
    """Test getting digital human details."""
    response = client.get(
        f"/api/v1/digital-human/{test_digital_human.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_digital_human.id
    assert data["name"] == test_digital_human.name
    assert data["description"] == test_digital_human.description


def test_get_digital_human_not_found(client, auth_token):
    """Test getting non-existent digital human."""
    response = client.get(
        "/api/v1/digital-human/99999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_digital_human(client, auth_token, test_digital_human):
    """Test deleting digital human."""
    with patch("pathlib.Path.exists", return_value=False):
        response = client.delete(
            f"/api/v1/digital-human/{test_digital_human.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

    # Verify it's deleted
    response = client.get(
        f"/api/v1/digital-human/{test_digital_human.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404


def test_delete_digital_human_not_found(client, auth_token):
    """Test deleting non-existent digital human."""
    response = client.delete(
        "/api/v1/digital-human/99999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_delete_digital_human_with_files(client, auth_token, test_digital_human, test_engine, tmp_path):
    """Test deleting digital human with associated files."""
    # Create fake files
    image_path = tmp_path / "image.jpg"
    video_path = tmp_path / "video.mp4"
    image_path.write_bytes(b"fake image")
    video_path.write_bytes(b"fake video")

    # Update digital human in database
    TestingSessionLocal = sessionmaker(bind=test_engine)
    session = TestingSessionLocal()
    dh = session.query(DigitalHuman).filter(DigitalHuman.id == test_digital_human.id).first()
    dh.image_path = str(image_path)
    dh.video_path = str(video_path)
    session.commit()
    session.close()

    response = client.delete(
        f"/api/v1/digital-human/{test_digital_human.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    # Verify files were deleted
    assert not image_path.exists()
    assert not video_path.exists()


def test_generate_video_exception_handling(test_db, test_user, test_digital_human):
    """Test video generation exception handling."""
    # Create a client with a video generator that raises an exception
    app = create_app()

    def override_get_db():
        session = test_db()
        try:
            yield session
        finally:
            session.close()

    def override_get_current_user():
        return test_user

    def override_get_video_generator():
        mock_gen = Mock()
        mock_gen.generate_from_text = Mock(side_effect=Exception("Test error"))
        mock_gen.mode = None
        return mock_gen

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_video_generator] = override_get_video_generator

    client = TestClient(app)
    auth_token = create_access_token({"sub": test_user.username, "user_id": test_user.id})

    response = client.post(
        "/api/v1/digital-human/generate",
        headers={"Authorization": f"Bearer {auth_token}"},
        data={
            "digital_human_id": test_digital_human.id,
            "text": "Hello world",
            "mode": "lipsync"
        }
    )

    assert response.status_code == 500
    assert "Video generation failed" in response.json()["detail"]
    assert "Test error" in response.json()["detail"]


def test_get_db_session():
    """Test get_db_session dependency function."""
    from src.api.digital_human import get_db_session

    # This will test the actual function, not the override
    gen = get_db_session()
    session = next(gen)
    assert session is not None
    # Clean up
    try:
        next(gen)
    except StopIteration:
        pass


def test_get_video_generator_dependency():
    """Test get_video_generator dependency function."""
    from src.api.digital_human import get_video_generator

    generator = get_video_generator()
    assert generator is not None
    assert isinstance(generator, VideoGenerator)
