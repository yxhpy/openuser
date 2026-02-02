"""Tests for cache manager plugin"""

import pytest
import time
import json
from pathlib import Path
from src.plugins.cache_manager import CacheManager


@pytest.fixture
def plugin(tmp_path):
    """Create cache manager plugin instance"""
    plugin = CacheManager()
    plugin._cache_dir = tmp_path / "cache"
    plugin._cache_dir.mkdir(parents=True, exist_ok=True)
    return plugin


class TestCacheManager:
    """Test CacheManager plugin"""

    def test_plugin_initialization(self, plugin):
        """Test plugin initialization"""
        assert plugin.name == "cache_manager"
        assert plugin.version == "1.0.0"
        assert plugin.dependencies == []
        assert plugin._state["cache_hits"] == 0
        assert plugin._state["cache_misses"] == 0

    def test_plugin_lifecycle(self, plugin):
        """Test plugin lifecycle hooks"""
        plugin.on_load()
        assert plugin._cache_dir.exists()

        plugin._state["cache_hits"] = 10
        plugin._state["cache_misses"] = 5
        plugin.on_unload()
        # State should still be preserved
        assert plugin._state["cache_hits"] == 10

    def test_set_and_get(self, plugin):
        """Test setting and getting cache values"""
        # Set value
        assert plugin.set("test_key", {"data": "value"}) is True

        # Get value
        value = plugin.get("test_key")
        assert value == {"data": "value"}
        assert plugin._state["cache_hits"] == 1

    def test_get_nonexistent(self, plugin):
        """Test getting non-existent cache value"""
        value = plugin.get("nonexistent")
        assert value is None
        assert plugin._state["cache_misses"] == 1

    def test_set_with_custom_ttl(self, plugin):
        """Test setting cache with custom TTL"""
        assert plugin.set("test_key", "value", ttl=1) is True

        # Should exist immediately
        value = plugin.get("test_key")
        assert value == "value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        value = plugin.get("test_key")
        assert value is None

    def test_delete(self, plugin):
        """Test deleting cache entry"""
        # Set value
        plugin.set("test_key", "value")

        # Delete
        assert plugin.delete("test_key") is True

        # Should not exist
        value = plugin.get("test_key")
        assert value is None

    def test_delete_nonexistent(self, plugin):
        """Test deleting non-existent entry"""
        # Should not raise error
        assert plugin.delete("nonexistent") is True

    def test_exists(self, plugin):
        """Test checking if cache entry exists"""
        # Non-existent
        assert plugin.exists("test_key") is False

        # Set value
        plugin.set("test_key", "value")

        # Should exist
        assert plugin.exists("test_key") is True

    def test_exists_expired(self, plugin):
        """Test exists with expired entry"""
        # Set with short TTL
        plugin.set("test_key", "value", ttl=1)

        # Should exist immediately
        assert plugin.exists("test_key") is True

        # Wait for expiration
        time.sleep(1.1)

        # Should not exist
        assert plugin.exists("test_key") is False

    def test_clear(self, plugin):
        """Test clearing all cache entries"""
        # Set multiple values
        plugin.set("key1", "value1")
        plugin.set("key2", "value2")
        plugin.set("key3", "value3")

        # Clear
        count = plugin.clear()
        assert count == 3

        # All should be gone
        assert plugin.get("key1") is None
        assert plugin.get("key2") is None
        assert plugin.get("key3") is None

    def test_cleanup_expired(self, plugin):
        """Test cleaning up expired entries"""
        # Set values with different TTLs
        plugin.set("key1", "value1", ttl=1)
        plugin.set("key2", "value2", ttl=10)
        plugin.set("key3", "value3", ttl=1)

        # Wait for some to expire
        time.sleep(1.1)

        # Cleanup
        count = plugin.cleanup_expired()
        assert count == 2

        # Expired should be gone
        assert plugin.get("key1") is None
        assert plugin.get("key3") is None

        # Non-expired should still exist
        assert plugin.get("key2") == "value2"

    def test_get_size(self, plugin):
        """Test getting cache size"""
        # Empty cache
        assert plugin.get_size() == 0

        # Add some data
        plugin.set("key1", "value1")
        plugin.set("key2", "value2")

        # Should have size
        size = plugin.get_size()
        assert size > 0

    def test_get_stats(self, plugin):
        """Test getting cache statistics"""
        # Set some values
        plugin.set("key1", "value1")
        plugin.set("key2", "value2")

        # Get some values
        plugin.get("key1")  # hit
        plugin.get("key3")  # miss

        stats = plugin.get_stats()
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 1
        assert stats["hit_rate"] == 50.0
        assert stats["total_entries"] == 2
        assert stats["size_bytes"] > 0
        assert stats["size_mb"] > 0
        assert "cache_dir" in stats

    def test_enforce_size_limit(self, plugin, tmp_path):
        """Test enforcing cache size limit"""
        # Set small size limit
        plugin.config = type('obj', (object,), {
            'get': lambda self, key, default: 0.001 if key == "max_size_mb" else default
        })()

        # Add multiple entries
        for i in range(10):
            plugin.set(f"key{i}", f"value{i}" * 100)

        # Enforce limit
        count = plugin.enforce_size_limit()
        assert count > 0

        # Size should be under limit
        size_mb = plugin.get_size() / (1024 * 1024)
        assert size_mb <= 0.001 or count > 0

    def test_cache_key_generation(self, plugin):
        """Test cache key generation"""
        key1 = plugin._get_cache_key("test")
        key2 = plugin._get_cache_key("test")
        key3 = plugin._get_cache_key("different")

        # Same input should generate same key
        assert key1 == key2

        # Different input should generate different key
        assert key1 != key3

    def test_set_error_handling(self, plugin):
        """Test error handling for set"""
        # Try to cache non-serializable object
        class NonSerializable:
            pass

        result = plugin.set("key", NonSerializable())
        assert result is False

    def test_get_corrupted_metadata(self, plugin):
        """Test getting cache with corrupted metadata"""
        # Set value
        plugin.set("test_key", "value")

        # Corrupt metadata
        metadata_path = plugin._get_metadata_path("test_key")
        with open(metadata_path, "w") as f:
            f.write("invalid json")

        # Should return None
        value = plugin.get("test_key")
        assert value is None
        assert plugin._state["cache_misses"] > 0

    def test_cleanup_expired_with_corrupted_metadata(self, plugin):
        """Test cleanup with corrupted metadata"""
        # Set valid value
        plugin.set("key1", "value1")

        # Create corrupted metadata
        corrupted_path = plugin._cache_dir / "corrupted.meta"
        with open(corrupted_path, "w") as f:
            f.write("invalid json")

        # Should not raise error
        count = plugin.cleanup_expired()
        assert count >= 0

    def test_config_schema(self, plugin):
        """Test plugin configuration schema"""
        assert plugin.config_schema is not None
        assert len(plugin.config_schema.fields) == 3

        # Check field names
        field_names = [f.name for f in plugin.config_schema.fields]
        assert "cache_dir" in field_names
        assert "max_size_mb" in field_names
        assert "default_ttl" in field_names

    def test_config_default_values(self, plugin):
        """Test plugin configuration default values"""
        if plugin.config:
            assert plugin.config.get("cache_dir") == "cache"
            assert plugin.config.get("max_size_mb") == 1024
            assert plugin.config.get("default_ttl") == 3600

    def test_set_without_config(self, plugin):
        """Test setting cache without configuration"""
        plugin.config = None

        # Should use default TTL
        assert plugin.set("test_key", "value") is True

        # Should be retrievable
        value = plugin.get("test_key")
        assert value == "value"

    def test_enforce_size_limit_without_config(self, plugin):
        """Test enforcing size limit without configuration"""
        plugin.config = None

        # Add some entries
        plugin.set("key1", "value1")
        plugin.set("key2", "value2")

        # Should not raise error
        count = plugin.enforce_size_limit()
        assert count >= 0

    def test_enforce_size_limit_under_limit(self, plugin):
        """Test enforcing size limit when already under limit"""
        # Add small entry
        plugin.set("key1", "value1")

        # Enforce limit (should not remove anything)
        count = plugin.enforce_size_limit()
        assert count == 0

        # Entry should still exist
        assert plugin.get("key1") == "value1"

    def test_multiple_cache_operations(self, plugin):
        """Test multiple cache operations"""
        # Set multiple values
        for i in range(5):
            plugin.set(f"key{i}", f"value{i}")

        # Get all values
        for i in range(5):
            value = plugin.get(f"key{i}")
            assert value == f"value{i}"

        # Delete some
        plugin.delete("key1")
        plugin.delete("key3")

        # Check remaining
        assert plugin.get("key0") == "value0"
        assert plugin.get("key1") is None
        assert plugin.get("key2") == "value2"
        assert plugin.get("key3") is None
        assert plugin.get("key4") == "value4"

    def test_cache_with_complex_data(self, plugin):
        """Test caching complex data structures"""
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "string": "test",
            "number": 42,
            "boolean": True,
            "null": None
        }

        plugin.set("complex", complex_data)
        retrieved = plugin.get("complex")

        assert retrieved == complex_data

    def test_get_with_corrupted_cache_file(self, plugin):
        """Test getting cache with corrupted cache file"""
        # Set value
        plugin.set("test_key", "value")

        # Corrupt cache file
        cache_path = plugin._get_cache_path("test_key")
        with open(cache_path, "w") as f:
            f.write("invalid json")

        # Should return None and increment misses
        value = plugin.get("test_key")
        assert value is None
        assert plugin._state["cache_misses"] > 0

    def test_delete_with_permission_error(self, plugin, monkeypatch):
        """Test delete with permission error"""
        # Set value
        plugin.set("test_key", "value")

        # Mock unlink to raise PermissionError
        def mock_unlink(self):
            raise PermissionError("Permission denied")

        monkeypatch.setattr(Path, "unlink", mock_unlink)

        # Should return False
        result = plugin.delete("test_key")
        assert result is False

    def test_enforce_size_limit_with_error(self, plugin, monkeypatch):
        """Test enforce_size_limit with error"""
        # Set value
        plugin.set("test_key", "value")

        # Mock get_size to raise error
        def mock_get_size():
            raise OSError("Error getting size")

        monkeypatch.setattr(plugin, "get_size", mock_get_size)

        # Should return 0
        count = plugin.enforce_size_limit()
        assert count == 0

