"""
Unit tests for Voice API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.api.main import app
from src.models.voice_cloning import VoiceProfile


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_synthesizer():
    """Create mock VoiceSynthesizer."""
    # Clear the LRU cache before mocking
    from src.api.dependencies import get_voice_synthesizer
    get_voice_synthesizer.cache_clear()

    with patch("src.api.dependencies.VoiceSynthesizer") as mock_class:
        synthesizer = Mock()
        synthesizer.synthesize.return_value = "/tmp/test_audio.wav"
        mock_class.return_value = synthesizer
        yield synthesizer

    # Clear cache after test
    get_voice_synthesizer.cache_clear()


@pytest.fixture
def mock_cloner():
    """Create mock VoiceCloner."""
    # Clear the LRU cache before mocking
    from src.api.dependencies import get_voice_cloner
    get_voice_cloner.cache_clear()

    with patch("src.api.dependencies.VoiceCloner") as mock_class:
        cloner = Mock()
        mock_class.return_value = cloner
        yield cloner

    # Clear cache after test
    get_voice_cloner.cache_clear()


class TestVoiceSynthesizeEndpoint:
    """Tests for /api/v1/voice/synthesize endpoint."""

    def test_synthesize_success(self, client, mock_synthesizer):
        """Test successful voice synthesis."""
        response = client.post(
            "/api/v1/voice/synthesize",
            json={
                "text": "Hello world",
                "backend": "coqui",
                "device": "cpu"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["audio_path"] == "/tmp/test_audio.wav"
        assert data["backend"] == "coqui"
        assert data["text_length"] == 11
        assert "duration" in data

        mock_synthesizer.synthesize.assert_called_once_with(
            text="Hello world",
            speaker_wav=None
        )

    def test_synthesize_with_speaker_wav(self, client, mock_synthesizer):
        """Test synthesis with speaker audio."""
        response = client.post(
            "/api/v1/voice/synthesize",
            json={
                "text": "Hello world",
                "backend": "coqui",
                "device": "cpu",
                "speaker_wav": "/path/to/speaker.wav"
            }
        )

        assert response.status_code == 200
        mock_synthesizer.synthesize.assert_called_once_with(
            text="Hello world",
            speaker_wav="/path/to/speaker.wav"
        )

    def test_synthesize_invalid_backend(self, client):
        """Test synthesis with invalid backend."""
        response = client.post(
            "/api/v1/voice/synthesize",
            json={
                "text": "Hello world",
                "backend": "invalid",
                "device": "cpu"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_synthesize_invalid_device(self, client):
        """Test synthesis with invalid device."""
        response = client.post(
            "/api/v1/voice/synthesize",
            json={
                "text": "Hello world",
                "backend": "coqui",
                "device": "invalid"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_synthesize_empty_text(self, client):
        """Test synthesis with empty text."""
        response = client.post(
            "/api/v1/voice/synthesize",
            json={
                "text": "",
                "backend": "coqui",
                "device": "cpu"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_synthesize_value_error(self, client, mock_synthesizer):
        """Test synthesis with ValueError."""
        mock_synthesizer.synthesize.side_effect = ValueError("Invalid input")

        response = client.post(
            "/api/v1/voice/synthesize",
            json={
                "text": "Hello world",
                "backend": "coqui",
                "device": "cpu"
            }
        )

        assert response.status_code == 400
        assert "Invalid input" in response.json()["detail"]

    def test_synthesize_general_error(self, client, mock_synthesizer):
        """Test synthesis with general error."""
        mock_synthesizer.synthesize.side_effect = Exception("Synthesis failed")

        response = client.post(
            "/api/v1/voice/synthesize",
            json={
                "text": "Hello world",
                "backend": "coqui",
                "device": "cpu"
            }
        )

        assert response.status_code == 500
        assert "Synthesis failed" in response.json()["detail"]


class TestVoiceProfileEndpoints:
    """Tests for voice profile endpoints."""

    def test_create_profile_success(self, client, mock_cloner):
        """Test successful profile creation."""
        profile = VoiceProfile(
            name="test_profile",
            sample_paths=["/path/to/sample1.wav", "/path/to/sample2.wav"],
            description="Test profile",
            created_at="2026-02-02T12:00:00",
            metadata={"language": "en"}
        )
        mock_cloner.create_profile.return_value = profile

        response = client.post(
            "/api/v1/voice/profiles",
            json={
                "name": "test_profile",
                "sample_paths": ["/path/to/sample1.wav", "/path/to/sample2.wav"],
                "description": "Test profile",
                "metadata": {"language": "en"}
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test_profile"
        assert data["description"] == "Test profile"
        assert data["sample_count"] == 2
        assert data["created_at"] == "2026-02-02T12:00:00"
        assert data["metadata"] == {"language": "en"}

        mock_cloner.create_profile.assert_called_once()
        mock_cloner.save_profile.assert_called_once_with(profile)

    def test_create_profile_value_error(self, client, mock_cloner):
        """Test profile creation with ValueError."""
        mock_cloner.create_profile.side_effect = ValueError("Invalid samples")

        response = client.post(
            "/api/v1/voice/profiles",
            json={
                "name": "test_profile",
                "sample_paths": ["/path/to/sample.wav"]
            }
        )

        assert response.status_code == 400
        assert "Invalid samples" in response.json()["detail"]

    def test_create_profile_general_error(self, client, mock_cloner):
        """Test profile creation with general error."""
        mock_cloner.create_profile.side_effect = Exception("Creation failed")

        response = client.post(
            "/api/v1/voice/profiles",
            json={
                "name": "test_profile",
                "sample_paths": ["/path/to/sample.wav"]
            }
        )

        assert response.status_code == 500
        assert "Profile creation failed" in response.json()["detail"]

    def test_list_profiles_success(self, client, mock_cloner):
        """Test successful profile listing."""
        mock_cloner.list_profiles.return_value = ["profile1", "profile2", "profile3"]

        response = client.get("/api/v1/voice/profiles")

        assert response.status_code == 200
        data = response.json()
        assert data["profiles"] == ["profile1", "profile2", "profile3"]
        assert data["count"] == 3

    def test_list_profiles_empty(self, client, mock_cloner):
        """Test listing with no profiles."""
        mock_cloner.list_profiles.return_value = []

        response = client.get("/api/v1/voice/profiles")

        assert response.status_code == 200
        data = response.json()
        assert data["profiles"] == []
        assert data["count"] == 0

    def test_list_profiles_error(self, client, mock_cloner):
        """Test listing profiles with error."""
        mock_cloner.list_profiles.side_effect = Exception("List failed")

        response = client.get("/api/v1/voice/profiles")

        assert response.status_code == 500
        assert "Failed to list profiles" in response.json()["detail"]

    def test_get_profile_success(self, client, mock_cloner):
        """Test successful profile retrieval."""
        mock_cloner.get_profile_info.return_value = {
            "name": "test_profile",
            "description": "Test profile",
            "sample_count": 3,
            "created_at": "2026-02-02T12:00:00",
            "metadata": {"language": "en"}
        }

        response = client.get("/api/v1/voice/profiles/test_profile")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test_profile"
        assert data["description"] == "Test profile"
        assert data["sample_count"] == 3

    def test_get_profile_not_found(self, client, mock_cloner):
        """Test getting non-existent profile."""
        mock_cloner.get_profile_info.side_effect = FileNotFoundError()

        response = client.get("/api/v1/voice/profiles/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_profile_error(self, client, mock_cloner):
        """Test getting profile with error."""
        mock_cloner.get_profile_info.side_effect = Exception("Get failed")

        response = client.get("/api/v1/voice/profiles/test_profile")

        assert response.status_code == 500
        assert "Failed to get profile" in response.json()["detail"]

    def test_delete_profile_success(self, client, mock_cloner):
        """Test successful profile deletion."""
        mock_cloner.delete_profile.return_value = True

        response = client.delete("/api/v1/voice/profiles/test_profile")

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        mock_cloner.delete_profile.assert_called_once_with("test_profile")

    def test_delete_profile_not_found(self, client, mock_cloner):
        """Test deleting non-existent profile."""
        mock_cloner.delete_profile.return_value = False

        response = client.delete("/api/v1/voice/profiles/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_profile_error(self, client, mock_cloner):
        """Test deleting profile with error."""
        mock_cloner.delete_profile.side_effect = Exception("Delete failed")

        response = client.delete("/api/v1/voice/profiles/test_profile")

        assert response.status_code == 500
        assert "Failed to delete profile" in response.json()["detail"]


class TestRootEndpoints:
    """Tests for root endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OpenUser API"
        assert data["version"] == "0.1.0"
        assert data["docs"] == "/docs"

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
