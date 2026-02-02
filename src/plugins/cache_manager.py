"""
Cache Manager Plugin

Provides cache management utilities for the system.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import time
import hashlib
import shutil

from src.core.plugin_manager import Plugin
from src.core.plugin_config import (
    PluginConfigSchema,
    ConfigField,
    ConfigFieldType,
)


class CacheManager(Plugin):
    """Cache management plugin"""

    name = "cache_manager"
    version = "1.0.0"
    dependencies = []

    # Define configuration schema
    config_schema = PluginConfigSchema()
    config_schema.add_field(ConfigField(
        name="cache_dir",
        field_type=ConfigFieldType.STRING,
        default="cache",
        description="Directory for cache storage"
    ))
    config_schema.add_field(ConfigField(
        name="max_size_mb",
        field_type=ConfigFieldType.INTEGER,
        default=1024,
        description="Maximum cache size in MB",
        validator=lambda x: x > 0
    ))
    config_schema.add_field(ConfigField(
        name="default_ttl",
        field_type=ConfigFieldType.INTEGER,
        default=3600,
        description="Default TTL in seconds",
        validator=lambda x: x > 0
    ))

    def __init__(self) -> None:
        super().__init__()
        self._state["cache_hits"] = 0
        self._state["cache_misses"] = 0
        self._cache_dir: Optional[Path] = None

    def _get_config(self, key: str, default: Any) -> Any:
        """Helper to get config value safely"""
        if self.config:
            return self.config.get(key, default)
        return default

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        super().on_load()
        cache_dir = self._get_config("cache_dir", "cache")
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Cache manager plugin loaded. Cache dir: {self._cache_dir}")

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        super().on_unload()
        hits = self._state["cache_hits"]
        misses = self._state["cache_misses"]
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0
        self.logger.info(
            f"Cache manager plugin unloaded. "
            f"Hits: {hits}, Misses: {misses}, Hit rate: {hit_rate:.1f}%"
        )

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash"""
        return hashlib.sha256(key.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key"""
        cache_key = self._get_cache_key(key)
        return self._cache_dir / f"{cache_key}.cache"

    def _get_metadata_path(self, key: str) -> Path:
        """Get metadata file path for key"""
        cache_key = self._get_cache_key(key)
        return self._cache_dir / f"{cache_key}.meta"

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set cache value

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (None = use default)

        Returns:
            True if successful
        """
        try:
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)

            # Use default TTL if not specified
            if ttl is None:
                ttl = self._get_config("default_ttl", 3600)

            # Save value
            with open(cache_path, "w") as f:
                json.dump(value, f)

            # Save metadata
            metadata = {
                "key": key,
                "created_at": time.time(),
                "ttl": ttl,
                "expires_at": time.time() + ttl
            }
            with open(metadata_path, "w") as f:
                json.dump(metadata, f)

            self.logger.debug(f"Cached value for key: {key}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set cache: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Get cache value

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        try:
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)

            # Check if cache exists
            if not cache_path.exists() or not metadata_path.exists():
                self._state["cache_misses"] += 1
                return None

            # Load metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Check if expired
            if time.time() > metadata["expires_at"]:
                self.logger.debug(f"Cache expired for key: {key}")
                self.delete(key)
                self._state["cache_misses"] += 1
                return None

            # Load value
            with open(cache_path, "r") as f:
                value = json.load(f)

            self._state["cache_hits"] += 1
            self.logger.debug(f"Cache hit for key: {key}")
            return value

        except Exception as e:
            self.logger.error(f"Failed to get cache: {e}")
            self._state["cache_misses"] += 1
            return None

    def delete(self, key: str) -> bool:
        """
        Delete cache entry

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        try:
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)

            if cache_path.exists():
                cache_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()

            self.logger.debug(f"Deleted cache for key: {key}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete cache: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if cache entry exists and is valid

        Args:
            key: Cache key

        Returns:
            True if exists and not expired
        """
        value = self.get(key)
        return value is not None

    def clear(self) -> int:
        """
        Clear all cache entries

        Returns:
            Number of entries cleared
        """
        try:
            count = 0
            for file in self._cache_dir.glob("*.cache"):
                file.unlink()
                count += 1
            for file in self._cache_dir.glob("*.meta"):
                file.unlink()

            self.logger.info(f"Cleared {count} cache entries")
            return count

        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return 0

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries

        Returns:
            Number of entries removed
        """
        try:
            count = 0
            current_time = time.time()

            for metadata_path in self._cache_dir.glob("*.meta"):
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                    if current_time > metadata["expires_at"]:
                        # Delete both cache and metadata files
                        cache_key = metadata_path.stem
                        cache_path = self._cache_dir / f"{cache_key}.cache"

                        if cache_path.exists():
                            cache_path.unlink()
                        metadata_path.unlink()
                        count += 1

                except Exception as e:
                    self.logger.warning(f"Failed to process {metadata_path}: {e}")
                    continue

            self.logger.info(f"Cleaned up {count} expired cache entries")
            return count

        except Exception as e:
            self.logger.error(f"Failed to cleanup expired cache: {e}")
            return 0

    def get_size(self) -> int:
        """
        Get total cache size in bytes

        Returns:
            Total size in bytes
        """
        try:
            total_size = 0
            for file in self._cache_dir.glob("*"):
                if file.is_file():
                    total_size += file.stat().st_size
            return total_size

        except Exception as e:
            self.logger.error(f"Failed to get cache size: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        hits = self._state["cache_hits"]
        misses = self._state["cache_misses"]
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0

        cache_files = list(self._cache_dir.glob("*.cache"))
        size_bytes = self.get_size()
        size_mb = size_bytes / (1024 * 1024)

        return {
            "cache_hits": hits,
            "cache_misses": misses,
            "hit_rate": hit_rate,
            "total_entries": len(cache_files),
            "size_bytes": size_bytes,
            "size_mb": size_mb,
            "cache_dir": str(self._cache_dir)
        }

    def enforce_size_limit(self) -> int:
        """
        Enforce cache size limit by removing oldest entries

        Returns:
            Number of entries removed
        """
        try:
            max_size_mb = self._get_config("max_size_mb", 1024)
            max_size_bytes = max_size_mb * 1024 * 1024

            current_size = self.get_size()
            if current_size <= max_size_bytes:
                return 0

            # Get all cache files with their creation times
            cache_files = []
            for metadata_path in self._cache_dir.glob("*.meta"):
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    cache_files.append((
                        metadata["created_at"],
                        metadata_path.stem,
                        metadata["key"]
                    ))
                except Exception:
                    continue

            # Sort by creation time (oldest first)
            cache_files.sort()

            # Remove oldest entries until under limit
            count = 0
            for _, cache_key, key in cache_files:
                if current_size <= max_size_bytes:
                    break

                cache_path = self._cache_dir / f"{cache_key}.cache"
                metadata_path = self._cache_dir / f"{cache_key}.meta"

                # Get file sizes before deletion
                file_size = 0
                if cache_path.exists():
                    file_size += cache_path.stat().st_size
                if metadata_path.exists():
                    file_size += metadata_path.stat().st_size

                # Delete files
                self.delete(key)
                current_size -= file_size
                count += 1

            self.logger.info(f"Enforced size limit, removed {count} entries")
            return count

        except Exception as e:
            self.logger.error(f"Failed to enforce size limit: {e}")
            return 0
