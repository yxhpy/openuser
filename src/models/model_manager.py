"""
Model Manager for Digital Human Engine

This module provides centralized model management including:
- Model download and caching
- GPU/CPU device management
- Model versioning
- Batch processing optimization
"""

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import torch


class ModelInfo:
    """Model information container"""

    def __init__(
        self,
        name: str,
        version: str,
        url: str,
        checksum: str,
        size_mb: float,
        description: str = "",
        dependencies: Optional[List[str]] = None
    ):
        self.name = name
        self.version = version
        self.url = url
        self.checksum = checksum
        self.size_mb = size_mb
        self.description = description
        self.dependencies = dependencies or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "url": self.url,
            "checksum": self.checksum,
            "size_mb": self.size_mb,
            "description": self.description,
            "dependencies": self.dependencies
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        """Create from dictionary"""
        return cls(
            name=data["name"],
            version=data["version"],
            url=data["url"],
            checksum=data["checksum"],
            size_mb=data["size_mb"],
            description=data.get("description", ""),
            dependencies=data.get("dependencies", [])
        )


class ModelManager:
    """
    Centralized model management system

    Features:
    - Model download and caching
    - GPU/CPU device management
    - Model versioning
    - Batch processing optimization
    """

    def __init__(
        self,
        cache_dir: str = "~/.openuser/models",
        device: Optional[str] = None,
        max_cache_size_gb: float = 50.0
    ):
        """
        Initialize ModelManager

        Args:
            cache_dir: Directory for model cache
            device: Device to use ('cuda', 'cpu', or None for auto)
            max_cache_size_gb: Maximum cache size in GB
        """
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Device management
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.max_cache_size_gb = max_cache_size_gb

        # Model registry
        self.registry_path = self.cache_dir / "registry.json"
        self.registry: Dict[str, ModelInfo] = self._load_registry()

    def _load_registry(self) -> Dict[str, ModelInfo]:
        """Load model registry from disk"""
        if not self.registry_path.exists():
            return {}

        with open(self.registry_path, "r") as f:
            data = json.load(f)
            return {
                key: ModelInfo.from_dict(value)
                for key, value in data.items()
            }

    def _save_registry(self) -> None:
        """Save model registry to disk"""
        data = {
            key: model.to_dict()
            for key, model in self.registry.items()
        }
        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _get_cache_size_gb(self) -> float:
        """Get current cache size in GB"""
        total_size = 0
        for file_path in self.cache_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size / (1024 ** 3)

    def _cleanup_cache(self, required_space_gb: float) -> None:
        """
        Clean up cache to make space for new models

        Args:
            required_space_gb: Required space in GB
        """
        current_size = self._get_cache_size_gb()
        if current_size + required_space_gb <= self.max_cache_size_gb:
            return

        # Get all model files with their access times
        model_files = []
        for model_key, model_info in self.registry.items():
            model_path = self.get_model_path(model_info.name, model_info.version)
            if model_path and model_path.exists():
                atime = model_path.stat().st_atime
                model_files.append((atime, model_key, model_path, model_info.size_mb / 1024))

        # Sort by access time (oldest first)
        model_files.sort()

        # Remove oldest models until we have enough space
        space_to_free = (current_size + required_space_gb) - self.max_cache_size_gb
        freed_space = 0.0

        for _, model_key, model_path, size_gb in model_files:
            if freed_space >= space_to_free:
                break

            # Remove model file
            if model_path.is_file():
                model_path.unlink()
            elif model_path.is_dir():
                shutil.rmtree(model_path)

            # Remove from registry
            del self.registry[model_key]
            freed_space += size_gb

        self._save_registry()

    def register_model(self, model_info: ModelInfo) -> None:
        """
        Register a model in the registry

        Args:
            model_info: Model information
        """
        model_key = f"{model_info.name}:{model_info.version}"
        self.registry[model_key] = model_info
        self._save_registry()

    def get_model_path(self, name: str, version: str) -> Optional[Path]:
        """
        Get path to cached model

        Args:
            name: Model name
            version: Model version

        Returns:
            Path to model or None if not cached
        """
        model_key = f"{name}:{version}"
        if model_key not in self.registry:
            return None

        model_path = self.cache_dir / name / version
        if not model_path.exists():
            return None

        return model_path

    def is_model_cached(self, name: str, version: str) -> bool:
        """
        Check if model is cached

        Args:
            name: Model name
            version: Model version

        Returns:
            True if model is cached
        """
        return self.get_model_path(name, version) is not None

    def list_models(self) -> List[ModelInfo]:
        """
        List all registered models

        Returns:
            List of model information
        """
        return list(self.registry.values())

    def get_model_info(self, name: str, version: str) -> Optional[ModelInfo]:
        """
        Get model information

        Args:
            name: Model name
            version: Model version

        Returns:
            Model information or None if not found
        """
        model_key = f"{name}:{version}"
        return self.registry.get(model_key)

    def delete_model(self, name: str, version: str) -> bool:
        """
        Delete model from cache

        Args:
            name: Model name
            version: Model version

        Returns:
            True if model was deleted
        """
        model_path = self.get_model_path(name, version)
        if not model_path:
            return False

        # Remove model files
        if model_path.is_file():
            model_path.unlink()
        elif model_path.is_dir():
            shutil.rmtree(model_path)

        # Remove from registry
        model_key = f"{name}:{version}"
        if model_key in self.registry:
            del self.registry[model_key]
            self._save_registry()

        return True

    def get_device(self) -> str:
        """Get current device"""
        return self.device

    def set_device(self, device: str) -> None:
        """
        Set device for model inference

        Args:
            device: Device to use ('cuda' or 'cpu')
        """
        if device not in ["cuda", "cpu"]:
            raise ValueError(f"Invalid device: {device}")

        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available")

        self.device = device

    def get_device_info(self) -> Dict[str, Any]:
        """
        Get device information

        Returns:
            Dictionary with device information
        """
        info = {
            "device": self.device,
            "cuda_available": torch.cuda.is_available()
        }

        if torch.cuda.is_available():
            info["cuda_device_count"] = torch.cuda.device_count()
            info["cuda_device_name"] = torch.cuda.get_device_name(0)
            info["cuda_memory_allocated_gb"] = torch.cuda.memory_allocated(0) / (1024 ** 3)
            info["cuda_memory_reserved_gb"] = torch.cuda.memory_reserved(0) / (1024 ** 3)

        return info

    def clear_cache(self) -> None:
        """Clear all cached models"""
        for model_path in self.cache_dir.iterdir():
            if model_path.is_file() and model_path != self.registry_path:
                model_path.unlink()
            elif model_path.is_dir():
                shutil.rmtree(model_path)

        self.registry.clear()
        self._save_registry()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        return {
            "cache_dir": str(self.cache_dir),
            "cache_size_gb": self._get_cache_size_gb(),
            "max_cache_size_gb": self.max_cache_size_gb,
            "model_count": len(self.registry),
            "models": [
                {
                    "name": model.name,
                    "version": model.version,
                    "size_mb": model.size_mb
                }
                for model in self.registry.values()
            ]
        }

