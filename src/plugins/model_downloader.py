"""
Model Downloader Plugin

Auto-download AI models from remote repositories with progress tracking,
checksum verification, and caching.
"""

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

import requests
from tqdm import tqdm

from src.core.plugin_manager import Plugin
from src.core.plugin_config import (
    ConfigField,
    ConfigFieldType,
    PluginConfig,
    PluginConfigSchema,
)


class ModelDownloader(Plugin):
    """Plugin for downloading and managing AI models."""

    name = "model-downloader"
    version = "1.0.0"
    description = "Auto-download AI models with progress tracking and verification"
    dependencies: List[str] = []

    # Define configuration schema
    config_schema = PluginConfigSchema()
    config_schema.add_field(
        ConfigField(
            name="download_dir",
            field_type=ConfigFieldType.STRING,
            default="models",
            description="Directory to store downloaded models",
        )
    )
    config_schema.add_field(
        ConfigField(
            name="chunk_size",
            field_type=ConfigFieldType.INTEGER,
            default=8192,
            description="Download chunk size in bytes",
        )
    )
    config_schema.add_field(
        ConfigField(
            name="verify_checksum",
            field_type=ConfigFieldType.BOOLEAN,
            default=True,
            description="Verify file checksum after download",
        )
    )
    config_schema.add_field(
        ConfigField(
            name="timeout",
            field_type=ConfigFieldType.INTEGER,
            default=300,
            description="Download timeout in seconds",
        )
    )

    def __init__(self):
        """Initialize the model downloader plugin."""
        super().__init__()
        self._downloads: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            "total_downloads": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "total_bytes_downloaded": 0,
        }

    def _get_config(self, key: str, default: Any) -> Any:
        """Helper to get config value safely"""
        if self.config:
            return self.config.get(key, default)
        return default

    def on_load(self) -> None:
        """Called when the plugin is loaded."""
        super().on_load()
        download_dir = self._get_config("download_dir", "models")
        os.makedirs(download_dir, exist_ok=True)
        self.logger.info(f"Model downloader plugin loaded. Download dir: {download_dir}")

    def on_unload(self) -> None:
        """Called when the plugin is unloaded."""
        super().on_unload()
        stats = self.get_stats()
        self.logger.info(
            f"Model downloader plugin unloaded. "
            f"Total: {stats['total_downloads']}, "
            f"Success: {stats['successful_downloads']}, "
            f"Failed: {stats['failed_downloads']}"
        )

    def download(
        self,
        url: str,
        output_path: Optional[str] = None,
        checksum: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> str:
        """Download a model from a URL.

        Args:
            url: URL to download from
            output_path: Optional output path (auto-generated if not provided)
            checksum: Optional SHA256 checksum to verify
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            Path to the downloaded file

        Raises:
            ValueError: If download fails or checksum doesn't match
        """
        self._stats["total_downloads"] += 1

        # Generate output path if not provided
        if output_path is None:
            download_dir = self._get_config("download_dir", "models")
            filename = os.path.basename(urlparse(url).path)
            output_path = os.path.join(download_dir, filename)

        # Create parent directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Check if file already exists and checksum matches
        if os.path.exists(output_path):
            if checksum and self._get_config("verify_checksum", True):
                if self._verify_checksum(output_path, checksum):
                    self._stats["successful_downloads"] += 1
                    return output_path

        # Download the file
        try:
            timeout = self._get_config("timeout", 300)
            chunk_size = self._get_config("chunk_size", 8192)

            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            # Download with progress tracking
            downloaded = 0
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        self._stats["total_bytes_downloaded"] += len(chunk)

                        if progress_callback:
                            progress_callback(downloaded, total_size)

            # Verify checksum if provided
            if checksum and self._get_config("verify_checksum", True):
                if not self._verify_checksum(output_path, checksum):
                    os.remove(output_path)
                    self._stats["failed_downloads"] += 1
                    raise ValueError(f"Checksum verification failed for {output_path}")

            self._stats["successful_downloads"] += 1
            return output_path

        except ValueError:
            # Re-raise ValueError (checksum failure) without incrementing counter again
            raise
        except Exception as e:
            self._stats["failed_downloads"] += 1
            if os.path.exists(output_path):
                os.remove(output_path)
            raise ValueError(f"Failed to download {url}: {str(e)}")

    def download_with_progress(
        self,
        url: str,
        output_path: Optional[str] = None,
        checksum: Optional[str] = None,
    ) -> str:
        """Download a model with a progress bar.

        Args:
            url: URL to download from
            output_path: Optional output path
            checksum: Optional SHA256 checksum to verify

        Returns:
            Path to the downloaded file
        """
        # Generate output path if not provided
        if output_path is None:
            download_dir = self._get_config("download_dir", "models")
            filename = os.path.basename(urlparse(url).path)
            output_path = os.path.join(download_dir, filename)

        # Check if file already exists
        if os.path.exists(output_path):
            if checksum and self._get_config("verify_checksum", True):
                if self._verify_checksum(output_path, checksum):
                    return output_path

        # Download with tqdm progress bar
        with tqdm(unit="B", unit_scale=True, desc=os.path.basename(output_path)) as pbar:

            def progress_callback(current: int, total: int):
                if pbar.total != total:
                    pbar.total = total
                pbar.update(current - pbar.n)

            return self.download(url, output_path, checksum, progress_callback)

    def list_models(self) -> List[Dict[str, Any]]:
        """List all downloaded models.

        Returns:
            List of model information dictionaries
        """
        download_dir = self._get_config("download_dir", "models")
        models = []

        if not os.path.exists(download_dir):
            return models

        for root, _, files in os.walk(download_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, download_dir)
                size = os.path.getsize(file_path)

                models.append(
                    {
                        "name": rel_path,
                        "path": file_path,
                        "size": size,
                        "checksum": self._calculate_checksum(file_path),
                    }
                )

        return models

    def delete_model(self, name: str) -> bool:
        """Delete a downloaded model.

        Args:
            name: Model name (relative path in download directory)

        Returns:
            True if deleted successfully, False otherwise
        """
        download_dir = self._get_config("download_dir", "models")
        model_path = os.path.join(download_dir, name)

        if os.path.exists(model_path):
            if os.path.isfile(model_path):
                os.remove(model_path)
            else:
                shutil.rmtree(model_path)
            return True

        return False

    def get_model_path(self, name: str) -> Optional[str]:
        """Get the path to a downloaded model.

        Args:
            name: Model name (relative path in download directory)

        Returns:
            Path to the model if it exists, None otherwise
        """
        download_dir = self._get_config("download_dir", "models")
        model_path = os.path.join(download_dir, name)

        if os.path.exists(model_path):
            return model_path

        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get download statistics.

        Returns:
            Dictionary containing download statistics
        """
        return self._stats.copy()

    def _verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file checksum.

        Args:
            file_path: Path to the file
            expected_checksum: Expected SHA256 checksum

        Returns:
            True if checksum matches, False otherwise
        """
        actual_checksum = self._calculate_checksum(file_path)
        return actual_checksum.lower() == expected_checksum.lower()

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of a file.

        Args:
            file_path: Path to the file

        Returns:
            SHA256 checksum as hex string
        """
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
