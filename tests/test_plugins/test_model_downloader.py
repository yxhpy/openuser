"""
Tests for Model Downloader Plugin
"""

import hashlib
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from src.plugins.model_downloader import ModelDownloader


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def downloader(temp_dir):
    """Create a ModelDownloader instance for testing."""
    plugin = ModelDownloader()
    # Mock the config
    plugin.config = Mock()
    plugin.config.get = lambda key, default: {
        "download_dir": temp_dir,
        "chunk_size": 1024,
        "verify_checksum": True,
        "timeout": 30,
    }.get(key, default)
    return plugin


def test_plugin_metadata():
    """Test plugin metadata."""
    assert ModelDownloader.name == "model-downloader"
    assert ModelDownloader.version == "1.0.0"
    assert ModelDownloader.description
    assert ModelDownloader.dependencies == []


def test_config_schema():
    """Test configuration schema."""
    schema = ModelDownloader.config_schema
    assert len(schema.fields) == 4

    # Check field names
    field_names = [f.name for f in schema.fields]
    assert "download_dir" in field_names
    assert "chunk_size" in field_names
    assert "verify_checksum" in field_names
    assert "timeout" in field_names


def test_on_load(downloader, temp_dir):
    """Test plugin loading."""
    # Remove the directory to test creation
    os.rmdir(temp_dir)
    assert not os.path.exists(temp_dir)

    downloader.on_load()
    assert os.path.exists(temp_dir)


def test_on_unload(downloader):
    """Test plugin unloading."""
    downloader.on_unload()
    # Should not raise any exceptions


def test_download_success(downloader, temp_dir):
    """Test successful file download."""
    # Create mock response
    test_content = b"test model data"
    test_checksum = hashlib.sha256(test_content).hexdigest()

    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(test_content))}
    mock_response.iter_content = Mock(return_value=[test_content])
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        output_path = downloader.download(
            "https://example.com/model.bin",
            checksum=test_checksum,
        )

        assert os.path.exists(output_path)
        with open(output_path, "rb") as f:
            assert f.read() == test_content

        stats = downloader.get_stats()
        assert stats["total_downloads"] == 1
        assert stats["successful_downloads"] == 1
        assert stats["failed_downloads"] == 0


def test_download_with_custom_output_path(downloader, temp_dir):
    """Test download with custom output path."""
    test_content = b"test model data"
    test_checksum = hashlib.sha256(test_content).hexdigest()
    custom_path = os.path.join(temp_dir, "custom", "model.bin")

    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(test_content))}
    mock_response.iter_content = Mock(return_value=[test_content])
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        output_path = downloader.download(
            "https://example.com/model.bin",
            output_path=custom_path,
            checksum=test_checksum,
        )

        assert output_path == custom_path
        assert os.path.exists(custom_path)


def test_download_with_progress_callback(downloader, temp_dir):
    """Test download with progress callback."""
    test_content = b"test model data"
    test_checksum = hashlib.sha256(test_content).hexdigest()

    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(test_content))}
    mock_response.iter_content = Mock(return_value=[test_content])
    mock_response.raise_for_status = Mock()

    progress_calls = []

    def progress_callback(current, total):
        progress_calls.append((current, total))

    with patch("requests.get", return_value=mock_response):
        downloader.download(
            "https://example.com/model.bin",
            checksum=test_checksum,
            progress_callback=progress_callback,
        )

        assert len(progress_calls) > 0
        assert progress_calls[-1][0] == len(test_content)


def test_download_checksum_verification_failure(temp_dir):
    """Test download with checksum verification failure."""
    # Create a fresh downloader for this test
    downloader = ModelDownloader()
    downloader.config = Mock()
    downloader.config.get = lambda key, default: {
        "download_dir": temp_dir,
        "chunk_size": 1024,
        "verify_checksum": True,
        "timeout": 30,
    }.get(key, default)

    test_content = b"test model data"
    wrong_checksum = "0" * 64

    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(test_content))}
    mock_response.iter_content = Mock(return_value=[test_content])
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="Checksum verification failed"):
            downloader.download(
                "https://example.com/model.bin",
                checksum=wrong_checksum,
            )

        stats = downloader.get_stats()
        assert stats["failed_downloads"] == 1


def test_download_network_error(temp_dir):
    """Test download with network error."""
    # Create a fresh downloader for this test
    downloader = ModelDownloader()
    downloader.config = Mock()
    downloader.config.get = lambda key, default: {
        "download_dir": temp_dir,
        "chunk_size": 1024,
        "verify_checksum": True,
        "timeout": 30,
    }.get(key, default)

    with patch("requests.get", side_effect=requests.RequestException("Network error")):
        with pytest.raises(ValueError, match="Failed to download"):
            downloader.download("https://example.com/model.bin")

        stats = downloader.get_stats()
        assert stats["failed_downloads"] == 1


def test_download_existing_file_with_valid_checksum(downloader, temp_dir):
    """Test download when file already exists with valid checksum."""
    test_content = b"test model data"
    test_checksum = hashlib.sha256(test_content).hexdigest()

    # Create existing file
    output_path = os.path.join(temp_dir, "model.bin")
    with open(output_path, "wb") as f:
        f.write(test_content)

    # Should not download again
    with patch("requests.get") as mock_get:
        result_path = downloader.download(
            "https://example.com/model.bin",
            output_path=output_path,
            checksum=test_checksum,
        )

        assert result_path == output_path
        mock_get.assert_not_called()


def test_download_with_progress_bar(downloader, temp_dir):
    """Test download with progress bar."""
    test_content = b"test model data"
    test_checksum = hashlib.sha256(test_content).hexdigest()

    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(test_content))}
    mock_response.iter_content = Mock(return_value=[test_content])
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        output_path = downloader.download_with_progress(
            "https://example.com/model.bin",
            checksum=test_checksum,
        )

        assert os.path.exists(output_path)


def test_list_models_empty(downloader, temp_dir):
    """Test listing models when directory is empty."""
    models = downloader.list_models()
    assert models == []


def test_list_models(downloader, temp_dir):
    """Test listing downloaded models."""
    # Create test files
    test_files = [
        ("model1.bin", b"model 1 data"),
        ("subdir/model2.bin", b"model 2 data"),
    ]

    for name, content in test_files:
        file_path = os.path.join(temp_dir, name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)

    models = downloader.list_models()
    assert len(models) == 2

    # Check model information
    model_names = [m["name"] for m in models]
    assert "model1.bin" in model_names
    assert os.path.join("subdir", "model2.bin") in model_names

    for model in models:
        assert "path" in model
        assert "size" in model
        assert "checksum" in model
        assert os.path.exists(model["path"])


def test_delete_model_file(downloader, temp_dir):
    """Test deleting a model file."""
    # Create test file
    test_file = os.path.join(temp_dir, "model.bin")
    with open(test_file, "wb") as f:
        f.write(b"test data")

    assert os.path.exists(test_file)

    # Delete the model
    result = downloader.delete_model("model.bin")
    assert result is True
    assert not os.path.exists(test_file)


def test_delete_model_directory(downloader, temp_dir):
    """Test deleting a model directory."""
    # Create test directory
    test_dir = os.path.join(temp_dir, "model_dir")
    os.makedirs(test_dir)
    test_file = os.path.join(test_dir, "model.bin")
    with open(test_file, "wb") as f:
        f.write(b"test data")

    assert os.path.exists(test_dir)

    # Delete the model directory
    result = downloader.delete_model("model_dir")
    assert result is True
    assert not os.path.exists(test_dir)


def test_delete_nonexistent_model(downloader, temp_dir):
    """Test deleting a nonexistent model."""
    result = downloader.delete_model("nonexistent.bin")
    assert result is False


def test_get_model_path_exists(downloader, temp_dir):
    """Test getting path to existing model."""
    # Create test file
    test_file = os.path.join(temp_dir, "model.bin")
    with open(test_file, "wb") as f:
        f.write(b"test data")

    path = downloader.get_model_path("model.bin")
    assert path == test_file


def test_get_model_path_not_exists(downloader, temp_dir):
    """Test getting path to nonexistent model."""
    path = downloader.get_model_path("nonexistent.bin")
    assert path is None


def test_get_stats(downloader):
    """Test getting download statistics."""
    stats = downloader.get_stats()
    assert "total_downloads" in stats
    assert "successful_downloads" in stats
    assert "failed_downloads" in stats
    assert "total_bytes_downloaded" in stats


def test_calculate_checksum(downloader, temp_dir):
    """Test checksum calculation."""
    test_content = b"test data"
    test_file = os.path.join(temp_dir, "test.bin")
    with open(test_file, "wb") as f:
        f.write(test_content)

    checksum = downloader._calculate_checksum(test_file)
    expected = hashlib.sha256(test_content).hexdigest()
    assert checksum == expected


def test_verify_checksum_valid(downloader, temp_dir):
    """Test checksum verification with valid checksum."""
    test_content = b"test data"
    test_file = os.path.join(temp_dir, "test.bin")
    with open(test_file, "wb") as f:
        f.write(test_content)

    expected_checksum = hashlib.sha256(test_content).hexdigest()
    assert downloader._verify_checksum(test_file, expected_checksum) is True


def test_verify_checksum_invalid(downloader, temp_dir):
    """Test checksum verification with invalid checksum."""
    test_content = b"test data"
    test_file = os.path.join(temp_dir, "test.bin")
    with open(test_file, "wb") as f:
        f.write(test_content)

    wrong_checksum = "0" * 64
    assert downloader._verify_checksum(test_file, wrong_checksum) is False


def test_verify_checksum_case_insensitive(downloader, temp_dir):
    """Test checksum verification is case insensitive."""
    test_content = b"test data"
    test_file = os.path.join(temp_dir, "test.bin")
    with open(test_file, "wb") as f:
        f.write(test_content)

    checksum = hashlib.sha256(test_content).hexdigest()
    assert downloader._verify_checksum(test_file, checksum.upper()) is True
    assert downloader._verify_checksum(test_file, checksum.lower()) is True


def test_download_without_checksum_verification(temp_dir):
    """Test download without checksum verification."""
    plugin = ModelDownloader()
    plugin.config = Mock()
    plugin.config.get = lambda key, default: {
        "download_dir": temp_dir,
        "verify_checksum": False,
    }.get(key, default)

    test_content = b"test model data"
    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(test_content))}
    mock_response.iter_content = Mock(return_value=[test_content])
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        # Should succeed even with wrong checksum
        output_path = plugin.download(
            "https://example.com/model.bin",
            checksum="wrong_checksum",
        )

        assert os.path.exists(output_path)


def test_download_chunked_content(downloader, temp_dir):
    """Test download with chunked content."""
    chunks = [b"chunk1", b"chunk2", b"chunk3"]
    test_content = b"".join(chunks)
    test_checksum = hashlib.sha256(test_content).hexdigest()

    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(test_content))}
    mock_response.iter_content = Mock(return_value=chunks)
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        output_path = downloader.download(
            "https://example.com/model.bin",
            checksum=test_checksum,
        )

        assert os.path.exists(output_path)
        with open(output_path, "rb") as f:
            assert f.read() == test_content


def test_download_updates_stats(downloader, temp_dir):
    """Test that download updates statistics correctly."""
    test_content = b"test model data"
    test_checksum = hashlib.sha256(test_content).hexdigest()

    mock_response = Mock()
    mock_response.headers = {"content-length": str(len(test_content))}
    mock_response.iter_content = Mock(return_value=[test_content])
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        downloader.download(
            "https://example.com/model.bin",
            checksum=test_checksum,
        )

        stats = downloader.get_stats()
        assert stats["total_downloads"] == 1
        assert stats["successful_downloads"] == 1
        assert stats["total_bytes_downloaded"] == len(test_content)


def test_get_config_without_config():
    """Test _get_config when config is None."""
    downloader = ModelDownloader()
    downloader.config = None
    result = downloader._get_config("test_key", "default_value")
    assert result == "default_value"


def test_download_with_progress_existing_file(temp_dir):
    """Test download_with_progress when file already exists."""
    downloader = ModelDownloader()
    downloader.config = Mock()
    downloader.config.get = lambda key, default: {
        "download_dir": temp_dir,
        "verify_checksum": True,
    }.get(key, default)

    # Create existing file
    test_content = b"test model data"
    test_checksum = hashlib.sha256(test_content).hexdigest()
    output_path = os.path.join(temp_dir, "model.bin")
    with open(output_path, "wb") as f:
        f.write(test_content)

    # Should not download again
    with patch("requests.get") as mock_get:
        result_path = downloader.download_with_progress(
            "https://example.com/model.bin",
            output_path=output_path,
            checksum=test_checksum,
        )

        assert result_path == output_path
        mock_get.assert_not_called()


def test_list_models_nonexistent_directory():
    """Test listing models when download directory doesn't exist."""
    downloader = ModelDownloader()
    downloader.config = Mock()
    downloader.config.get = lambda key, default: {
        "download_dir": "/nonexistent/directory",
    }.get(key, default)

    models = downloader.list_models()
    assert models == []


def test_download_network_error_with_partial_file(temp_dir):
    """Test download with network error after partial file creation."""
    downloader = ModelDownloader()
    downloader.config = Mock()
    downloader.config.get = lambda key, default: {
        "download_dir": temp_dir,
        "chunk_size": 1024,
        "verify_checksum": True,
        "timeout": 30,
    }.get(key, default)

    output_path = os.path.join(temp_dir, "model.bin")

    # Create a mock response that raises an error during iteration
    mock_response = Mock()
    mock_response.headers = {"content-length": "1000"}
    mock_response.raise_for_status = Mock()

    def iter_with_error(chunk_size):
        # Create partial file first
        with open(output_path, "wb") as f:
            f.write(b"partial data")
        raise requests.RequestException("Connection lost")

    mock_response.iter_content = iter_with_error

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="Failed to download"):
            downloader.download("https://example.com/model.bin")

        # File should be cleaned up
        assert not os.path.exists(output_path)
        stats = downloader.get_stats()
        assert stats["failed_downloads"] == 1
