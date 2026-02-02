"""Tests for Voice Cloning module"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import torch

from src.models.voice_cloning import VoiceCloner, VoiceProfile


@pytest.fixture
def temp_profile_dir():
    """Create temporary profile directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_audio_files():
    """Create temporary audio files for testing"""
    files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            files.append(f.name)
    yield files
    # Cleanup
    for file in files:
        if os.path.exists(file):
            os.unlink(file)


@pytest.fixture
def voice_cloner(temp_profile_dir):
    """Create VoiceCloner instance"""
    return VoiceCloner(profile_dir=temp_profile_dir, min_samples=2)


def test_voice_profile_creation():
    """Test VoiceProfile dataclass creation"""
    profile = VoiceProfile(
        name="test_profile",
        description="Test profile",
        sample_paths=["/path/to/sample1.wav", "/path/to/sample2.wav"],
    )

    assert profile.name == "test_profile"
    assert profile.description == "Test profile"
    assert len(profile.sample_paths) == 2
    assert profile.created_at != ""
    assert profile.updated_at != ""
    assert profile.metadata == {}


def test_voice_profile_with_metadata():
    """Test VoiceProfile with custom metadata"""
    metadata = {"language": "en", "gender": "male"}
    profile = VoiceProfile(
        name="test",
        description="Test",
        sample_paths=[],
        metadata=metadata,
    )

    assert profile.metadata == metadata


def test_voice_cloner_init(temp_profile_dir):
    """Test VoiceCloner initialization"""
    cloner = VoiceCloner(profile_dir=temp_profile_dir, min_samples=3)

    assert cloner.profile_dir == Path(temp_profile_dir)
    assert cloner.min_samples == 3
    assert cloner.sample_rate == 22050
    assert cloner.profile_dir.exists()


def test_voice_cloner_device_selection():
    """Test device selection based on CUDA availability"""
    with patch("torch.cuda.is_available", return_value=True):
        cloner = VoiceCloner(device="cuda")
        assert cloner.device == "cuda"

    with patch("torch.cuda.is_available", return_value=False):
        cloner = VoiceCloner(device="cuda")
        assert cloner.device == "cpu"


def test_validate_audio_samples_success(voice_cloner, temp_audio_files):
    """Test successful audio sample validation"""
    result = voice_cloner.validate_audio_samples(temp_audio_files)
    assert result is True


def test_validate_audio_samples_too_few(voice_cloner):
    """Test validation failure with too few samples"""
    with pytest.raises(ValueError, match="At least 2 samples required"):
        voice_cloner.validate_audio_samples(["/path/to/sample.wav"])


def test_validate_audio_samples_file_not_found(voice_cloner):
    """Test validation failure when file doesn't exist"""
    with pytest.raises(ValueError, match="Sample file not found"):
        voice_cloner.validate_audio_samples(
            ["/nonexistent/file1.wav", "/nonexistent/file2.wav"]
        )


def test_validate_audio_samples_unsupported_format(voice_cloner, temp_audio_files):
    """Test validation failure with unsupported format"""
    # Create a file with unsupported extension
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"not audio")
        unsupported_file = f.name

    try:
        with pytest.raises(ValueError, match="Unsupported audio format"):
            voice_cloner.validate_audio_samples([unsupported_file, temp_audio_files[0]])
    finally:
        os.unlink(unsupported_file)


def test_create_profile_success(voice_cloner, temp_audio_files):
    """Test successful profile creation"""
    profile = voice_cloner.create_profile(
        name="test_voice",
        sample_paths=temp_audio_files,
        description="Test voice profile",
        metadata={"language": "en"},
    )

    assert profile.name == "test_voice"
    assert profile.description == "Test voice profile"
    assert profile.sample_paths == temp_audio_files
    assert profile.metadata["language"] == "en"

    # Check if profile file was created
    profile_path = voice_cloner.profile_dir / "test_voice.json"
    assert profile_path.exists()


def test_create_profile_already_exists(voice_cloner, temp_audio_files):
    """Test profile creation failure when profile already exists"""
    voice_cloner.create_profile("test_voice", temp_audio_files)

    with pytest.raises(ValueError, match="Profile 'test_voice' already exists"):
        voice_cloner.create_profile("test_voice", temp_audio_files)


def test_create_profile_invalid_samples(voice_cloner):
    """Test profile creation failure with invalid samples"""
    with pytest.raises(ValueError, match="At least 2 samples required"):
        voice_cloner.create_profile("test", ["/path/to/sample.wav"])


def test_save_and_load_profile(voice_cloner, temp_audio_files):
    """Test saving and loading profile"""
    original = voice_cloner.create_profile(
        name="test_voice",
        sample_paths=temp_audio_files,
        description="Test profile",
    )

    loaded = voice_cloner.load_profile("test_voice")

    assert loaded.name == original.name
    assert loaded.description == original.description
    assert loaded.sample_paths == original.sample_paths


def test_load_profile_not_found(voice_cloner):
    """Test loading non-existent profile"""
    with pytest.raises(FileNotFoundError, match="Profile 'nonexistent' not found"):
        voice_cloner.load_profile("nonexistent")


def test_list_profiles(voice_cloner, temp_audio_files):
    """Test listing profiles"""
    assert voice_cloner.list_profiles() == []

    voice_cloner.create_profile("profile1", temp_audio_files)
    voice_cloner.create_profile("profile2", temp_audio_files)

    profiles = voice_cloner.list_profiles()
    assert len(profiles) == 2
    assert "profile1" in profiles
    assert "profile2" in profiles


def test_delete_profile_success(voice_cloner, temp_audio_files):
    """Test successful profile deletion"""
    voice_cloner.create_profile("test_voice", temp_audio_files)
    assert "test_voice" in voice_cloner.list_profiles()

    result = voice_cloner.delete_profile("test_voice")
    assert result is True
    assert "test_voice" not in voice_cloner.list_profiles()


def test_delete_profile_not_found(voice_cloner):
    """Test deleting non-existent profile"""
    with pytest.raises(FileNotFoundError, match="Profile 'nonexistent' not found"):
        voice_cloner.delete_profile("nonexistent")


def test_update_profile_description(voice_cloner, temp_audio_files):
    """Test updating profile description"""
    voice_cloner.create_profile("test_voice", temp_audio_files, description="Old")

    updated = voice_cloner.update_profile("test_voice", description="New description")

    assert updated.description == "New description"
    assert updated.sample_paths == temp_audio_files


def test_update_profile_samples(voice_cloner, temp_audio_files):
    """Test updating profile samples"""
    voice_cloner.create_profile("test_voice", temp_audio_files[:2])

    updated = voice_cloner.update_profile("test_voice", sample_paths=temp_audio_files)

    assert updated.sample_paths == temp_audio_files


def test_update_profile_metadata(voice_cloner, temp_audio_files):
    """Test updating profile metadata"""
    voice_cloner.create_profile("test_voice", temp_audio_files, metadata={"lang": "en"})

    updated = voice_cloner.update_profile("test_voice", metadata={"gender": "male"})

    assert updated.metadata["lang"] == "en"
    assert updated.metadata["gender"] == "male"


def test_update_profile_not_found(voice_cloner):
    """Test updating non-existent profile"""
    with pytest.raises(FileNotFoundError, match="Profile 'nonexistent' not found"):
        voice_cloner.update_profile("nonexistent", description="New")


def test_update_profile_invalid_samples(voice_cloner, temp_audio_files):
    """Test updating profile with invalid samples"""
    voice_cloner.create_profile("test_voice", temp_audio_files)

    with pytest.raises(ValueError, match="At least 2 samples required"):
        voice_cloner.update_profile("test_voice", sample_paths=["/path/to/sample.wav"])


def test_get_profile_info(voice_cloner, temp_audio_files):
    """Test getting profile information"""
    voice_cloner.create_profile(
        "test_voice",
        temp_audio_files,
        description="Test profile",
        metadata={"language": "en"},
    )

    info = voice_cloner.get_profile_info("test_voice")

    assert info["name"] == "test_voice"
    assert info["description"] == "Test profile"
    assert info["num_samples"] == 3
    assert "created_at" in info
    assert "updated_at" in info
    assert info["metadata"]["language"] == "en"


def test_get_profile_info_not_found(voice_cloner):
    """Test getting info for non-existent profile"""
    with pytest.raises(FileNotFoundError, match="Profile 'nonexistent' not found"):
        voice_cloner.get_profile_info("nonexistent")


def test_validate_supported_audio_formats(voice_cloner):
    """Test validation with all supported audio formats"""
    formats = [".wav", ".mp3", ".flac", ".ogg"]

    for fmt in formats:
        files = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(suffix=fmt, delete=False) as f:
                f.write(b"fake audio")
                files.append(f.name)

        try:
            result = voice_cloner.validate_audio_samples(files)
            assert result is True
        finally:
            for file in files:
                os.unlink(file)




