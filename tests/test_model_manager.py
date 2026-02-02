"""
Tests for Model Manager module.
"""

import hashlib
import json
import shutil
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, mock_open

import pytest
import torch

from src.models.model_manager import ModelInfo, ModelManager


class TestModelInfo:
    """Test cases for ModelInfo class."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        model_info = ModelInfo(
            name="test-model",
            version="1.0.0",
            url="https://example.com/model.pth",
            checksum="abc123",
            size_mb=100.0
        )

        assert model_info.name == "test-model"
        assert model_info.version == "1.0.0"
        assert model_info.url == "https://example.com/model.pth"
        assert model_info.checksum == "abc123"
        assert model_info.size_mb == 100.0
        assert model_info.description == ""
        assert model_info.dependencies == []

    def test_init_custom(self):
        """Test initialization with custom parameters."""
        model_info = ModelInfo(
            name="test-model",
            version="1.0.0",
            url="https://example.com/model.pth",
            checksum="abc123",
            size_mb=100.0,
            description="Test model description",
            dependencies=["dep1", "dep2"]
        )
        assert model_info.name == "test-model"
        assert model_info.version == "1.0.0"
        assert model_info.url == "https://example.com/model.pth"
        assert model_info.checksum == "abc123"
        assert model_info.size_mb == 100.0
        assert model_info.description == "Test model description"
        assert model_info.dependencies == ["dep1", "dep2"]

    def test_to_dict(self):
        """Test conversion to dictionary."""
        model_info = ModelInfo(
            name="test-model",
            version="1.0.0",
            url="https://example.com/model.pth",
            checksum="abc123",
            size_mb=100.0,
            description="Test model",
            dependencies=["dep1"]
        )

        result = model_info.to_dict()

        assert result == {
            "name": "test-model",
            "version": "1.0.0",
            "url": "https://example.com/model.pth",
            "checksum": "abc123",
            "size_mb": 100.0,
            "description": "Test model",
            "dependencies": ["dep1"]
        }

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "name": "test-model",
            "version": "1.0.0",
            "url": "https://example.com/model.pth",
            "checksum": "abc123",
            "size_mb": 100.0,
            "description": "Test model",
            "dependencies": ["dep1"]
        }

        model_info = ModelInfo.from_dict(data)

        assert model_info.name == "test-model"
        assert model_info.version == "1.0.0"
        assert model_info.url == "https://example.com/model.pth"
        assert model_info.checksum == "abc123"
        assert model_info.size_mb == 100.0
        assert model_info.description == "Test model"
        assert model_info.dependencies == ["dep1"]

    def test_from_dict_minimal(self):
        """Test creation from dictionary with minimal fields."""
        data = {
            "name": "test-model",
            "version": "1.0.0",
            "url": "https://example.com/model.pth",
            "checksum": "abc123",
            "size_mb": 100.0
        }

        model_info = ModelInfo.from_dict(data)

        assert model_info.name == "test-model"
        assert model_info.description == ""
        assert model_info.dependencies == []


class TestModelManager:
    """Test cases for ModelManager class."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def model_manager(self, temp_cache_dir):
        """Create ModelManager instance with temporary cache."""
        return ModelManager(cache_dir=temp_cache_dir, device="cpu")

    @pytest.fixture
    def sample_model_info(self):
        """Create sample model info."""
        return ModelInfo(
            name="test-model",
            version="1.0.0",
            url="https://example.com/model.pth",
            checksum="abc123",
            size_mb=100.0,
            description="Test model"
        )

    def test_init_default_device(self, temp_cache_dir):
        """Test initialization with default device."""
        manager = ModelManager(cache_dir=temp_cache_dir)

        expected_device = "cuda" if torch.cuda.is_available() else "cpu"
        assert manager.device == expected_device
        assert manager.cache_dir.exists()
        assert manager.max_cache_size_gb == 50.0

    def test_init_custom_device(self, temp_cache_dir):
        """Test initialization with custom device."""
        manager = ModelManager(cache_dir=temp_cache_dir, device="cpu")

        assert manager.device == "cpu"

    def test_init_creates_cache_dir(self, temp_cache_dir):
        """Test that initialization creates cache directory."""
        cache_path = Path(temp_cache_dir) / "subdir"
        manager = ModelManager(cache_dir=str(cache_path))

        assert cache_path.exists()

    def test_load_registry_empty(self, model_manager):
        """Test loading empty registry."""
        assert len(model_manager.registry) == 0

    def test_load_registry_existing(self, temp_cache_dir):
        """Test loading existing registry."""
        registry_path = Path(temp_cache_dir) / "registry.json"
        registry_data = {
            "test-model:1.0.0": {
                "name": "test-model",
                "version": "1.0.0",
                "url": "https://example.com/model.pth",
                "checksum": "abc123",
                "size_mb": 100.0,
                "description": "Test model",
                "dependencies": []
            }
        }

        with open(registry_path, "w") as f:
            json.dump(registry_data, f)

        manager = ModelManager(cache_dir=temp_cache_dir)

        assert len(manager.registry) == 1
        assert "test-model:1.0.0" in manager.registry

    def test_save_registry(self, model_manager, sample_model_info):
        """Test saving registry to disk."""
        model_manager.register_model(sample_model_info)

        registry_path = model_manager.registry_path
        assert registry_path.exists()

        with open(registry_path, "r") as f:
            data = json.load(f)

        assert "test-model:1.0.0" in data

    def test_calculate_checksum(self, model_manager, temp_cache_dir):
        """Test checksum calculation."""
        test_file = Path(temp_cache_dir) / "test.txt"
        test_content = b"test content"
        test_file.write_bytes(test_content)

        checksum = model_manager._calculate_checksum(test_file)

        expected = hashlib.sha256(test_content).hexdigest()
        assert checksum == expected

    def test_get_cache_size_gb(self, model_manager, temp_cache_dir):
        """Test cache size calculation."""
        # Create test files
        test_file1 = Path(temp_cache_dir) / "file1.txt"
        test_file1.write_bytes(b"x" * 1024 * 1024)  # 1 MB

        test_file2 = Path(temp_cache_dir) / "file2.txt"
        test_file2.write_bytes(b"x" * 1024 * 1024)  # 1 MB

        size_gb = model_manager._get_cache_size_gb()

        # Should be approximately 2 MB = 0.002 GB (plus registry.json)
        assert size_gb > 0.001
        assert size_gb < 0.01

    def test_register_model(self, model_manager, sample_model_info):
        """Test model registration."""
        model_manager.register_model(sample_model_info)

        assert "test-model:1.0.0" in model_manager.registry
        assert model_manager.registry["test-model:1.0.0"].name == "test-model"

    def test_get_model_path_not_cached(self, model_manager):
        """Test getting path for non-cached model."""
        path = model_manager.get_model_path("nonexistent", "1.0.0")

        assert path is None

    def test_get_model_path_cached(self, model_manager, sample_model_info, temp_cache_dir):
        """Test getting path for cached model."""
        # Register model
        model_manager.register_model(sample_model_info)

        # Create model directory
        model_path = Path(temp_cache_dir) / "test-model" / "1.0.0"
        model_path.mkdir(parents=True)

        path = model_manager.get_model_path("test-model", "1.0.0")

        assert path is not None
        assert path == model_path

    def test_is_model_cached_false(self, model_manager):
        """Test checking if model is cached (not cached)."""
        assert not model_manager.is_model_cached("nonexistent", "1.0.0")

    def test_is_model_cached_true(self, model_manager, sample_model_info, temp_cache_dir):
        """Test checking if model is cached (cached)."""
        # Register model
        model_manager.register_model(sample_model_info)

        # Create model directory
        model_path = Path(temp_cache_dir) / "test-model" / "1.0.0"
        model_path.mkdir(parents=True)

        assert model_manager.is_model_cached("test-model", "1.0.0")

    def test_list_models_empty(self, model_manager):
        """Test listing models when empty."""
        models = model_manager.list_models()

        assert len(models) == 0

    def test_list_models(self, model_manager, sample_model_info):
        """Test listing models."""
        model_manager.register_model(sample_model_info)

        models = model_manager.list_models()

        assert len(models) == 1
        assert models[0].name == "test-model"

    def test_get_model_info_not_found(self, model_manager):
        """Test getting model info for non-existent model."""
        info = model_manager.get_model_info("nonexistent", "1.0.0")

        assert info is None

    def test_get_model_info(self, model_manager, sample_model_info):
        """Test getting model info."""
        model_manager.register_model(sample_model_info)

        info = model_manager.get_model_info("test-model", "1.0.0")

        assert info is not None
        assert info.name == "test-model"
        assert info.version == "1.0.0"

    def test_delete_model_not_found(self, model_manager):
        """Test deleting non-existent model."""
        result = model_manager.delete_model("nonexistent", "1.0.0")

        assert result is False

    def test_delete_model_file(self, model_manager, sample_model_info, temp_cache_dir):
        """Test deleting model file."""
        # Register model
        model_manager.register_model(sample_model_info)

        # Create model file
        model_path = Path(temp_cache_dir) / "test-model" / "1.0.0"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model_path.write_text("test")

        result = model_manager.delete_model("test-model", "1.0.0")

        assert result is True
        assert not model_path.exists()
        assert "test-model:1.0.0" not in model_manager.registry

    def test_delete_model_directory(self, model_manager, sample_model_info, temp_cache_dir):
        """Test deleting model directory."""
        # Register model
        model_manager.register_model(sample_model_info)

        # Create model directory
        model_path = Path(temp_cache_dir) / "test-model" / "1.0.0"
        model_path.mkdir(parents=True)
        (model_path / "file.txt").write_text("test")

        result = model_manager.delete_model("test-model", "1.0.0")

        assert result is True
        assert not model_path.exists()
        assert "test-model:1.0.0" not in model_manager.registry

    def test_get_device(self, model_manager):
        """Test getting device."""
        assert model_manager.get_device() == "cpu"

    def test_set_device_valid(self, model_manager):
        """Test setting valid device."""
        model_manager.set_device("cpu")

        assert model_manager.device == "cpu"

    def test_set_device_invalid(self, model_manager):
        """Test setting invalid device."""
        with pytest.raises(ValueError, match="Invalid device"):
            model_manager.set_device("invalid")

    @patch("torch.cuda.is_available", return_value=False)
    def test_set_device_cuda_not_available(self, mock_cuda, model_manager):
        """Test setting CUDA when not available."""
        with pytest.raises(RuntimeError, match="CUDA is not available"):
            model_manager.set_device("cuda")

    def test_get_device_info_cpu(self, model_manager):
        """Test getting device info for CPU."""
        info = model_manager.get_device_info()

        assert "device" in info
        assert "cuda_available" in info
        assert info["device"] == "cpu"

    @patch("torch.cuda.is_available", return_value=True)
    @patch("torch.cuda.device_count", return_value=1)
    @patch("torch.cuda.get_device_name", return_value="Test GPU")
    @patch("torch.cuda.memory_allocated", return_value=1024**3)
    @patch("torch.cuda.memory_reserved", return_value=2*1024**3)
    def test_get_device_info_cuda(
        self, mock_reserved, mock_allocated, mock_name, mock_count, mock_available, temp_cache_dir
    ):
        """Test getting device info for CUDA."""
        manager = ModelManager(cache_dir=temp_cache_dir, device="cuda")
        info = manager.get_device_info()

        assert info["device"] == "cuda"
        assert info["cuda_available"] is True
        assert info["cuda_device_count"] == 1
        assert info["cuda_device_name"] == "Test GPU"
        assert info["cuda_memory_allocated_gb"] == 1.0
        assert info["cuda_memory_reserved_gb"] == 2.0

    def test_clear_cache(self, model_manager, sample_model_info, temp_cache_dir):
        """Test clearing cache."""
        # Register model
        model_manager.register_model(sample_model_info)

        # Create model directory
        model_path = Path(temp_cache_dir) / "test-model" / "1.0.0"
        model_path.mkdir(parents=True)
        (model_path / "file.txt").write_text("test")

        # Create additional file
        test_file = Path(temp_cache_dir) / "test.txt"
        test_file.write_text("test")

        model_manager.clear_cache()

        assert len(model_manager.registry) == 0
        assert not model_path.exists()
        assert not test_file.exists()
        assert model_manager.registry_path.exists()  # Registry file should remain

    def test_get_cache_stats(self, model_manager, sample_model_info):
        """Test getting cache statistics."""
        model_manager.register_model(sample_model_info)

        stats = model_manager.get_cache_stats()

        assert "cache_dir" in stats
        assert "cache_size_gb" in stats
        assert "max_cache_size_gb" in stats
        assert "model_count" in stats
        assert "models" in stats
        assert stats["model_count"] == 1
        assert len(stats["models"]) == 1
        assert stats["models"][0]["name"] == "test-model"

    def test_cleanup_cache_no_cleanup_needed(self, model_manager, sample_model_info, temp_cache_dir):
        """Test cleanup when no cleanup is needed."""
        model_manager.register_model(sample_model_info)

        # Create small model file
        model_path = Path(temp_cache_dir) / "test-model" / "1.0.0"
        model_path.mkdir(parents=True)
        (model_path / "model.pth").write_bytes(b"x" * 1024)  # 1 KB

        initial_count = len(model_manager.registry)

        # Try to cleanup with large required space (should not remove anything)
        model_manager._cleanup_cache(0.001)  # 1 MB

        assert len(model_manager.registry) == initial_count

    def test_cleanup_cache_removes_oldest(self, model_manager, temp_cache_dir):
        """Test cleanup removes oldest models first."""
        # Create multiple models
        models = []
        for i in range(3):
            model_info = ModelInfo(
                name=f"model-{i}",
                version="1.0.0",
                url=f"https://example.com/model-{i}.pth",
                checksum=f"abc{i}",
                size_mb=10.0
            )
            models.append(model_info)
            model_manager.register_model(model_info)

            # Create model directory
            model_path = Path(temp_cache_dir) / f"model-{i}" / "1.0.0"
            model_path.mkdir(parents=True)
            (model_path / "model.pth").write_bytes(b"x" * 10 * 1024 * 1024)  # 10 MB

            # Sleep to ensure different access times
            time.sleep(0.01)

            # Access the file to update atime
            (model_path / "model.pth").stat()

        # Set max cache size to 25 MB
        model_manager.max_cache_size_gb = 0.025

        # Cleanup to make space for 15 MB (should remove oldest model)
        model_manager._cleanup_cache(0.015)

        # Should have removed at least one model
        assert len(model_manager.registry) < 3

    def test_get_model_path_registered_but_not_exists(self, model_manager, sample_model_info):
        """Test getting path for model that is registered but file doesn't exist."""
        # Register model without creating the actual file
        model_manager.register_model(sample_model_info)

        # Don't create the model directory
        path = model_manager.get_model_path("test-model", "1.0.0")

        assert path is None

    def test_cleanup_cache_removes_file(self, model_manager, temp_cache_dir):
        """Test cleanup removes model files (not directories)."""
        # Create a model as a file (not directory)
        model_info = ModelInfo(
            name="file-model",
            version="1.0.0",
            url="https://example.com/file-model.pth",
            checksum="abc123",
            size_mb=10.0
        )
        model_manager.register_model(model_info)

        # Create model as a file
        model_path = Path(temp_cache_dir) / "file-model" / "1.0.0"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        # Create as a file, not directory
        model_path.write_bytes(b"x" * 10 * 1024 * 1024)  # 10 MB

        # Set max cache size to 5 MB
        model_manager.max_cache_size_gb = 0.005

        # Cleanup to make space for 1 MB (should remove the file)
        model_manager._cleanup_cache(0.001)

        # Should have removed the model
        assert len(model_manager.registry) == 0
        assert not model_path.exists()
