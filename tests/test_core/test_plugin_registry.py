"""
Tests for Plugin Registry
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from src.core.plugin_registry import PluginMetadata, PluginRegistry


@pytest.fixture
def temp_registry_file():
    """Create a temporary registry file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def registry(temp_registry_file):
    """Create a PluginRegistry instance for testing."""
    return PluginRegistry(temp_registry_file)


@pytest.fixture
def sample_metadata():
    """Create sample plugin metadata for testing."""
    return PluginMetadata(
        name="test-plugin",
        version="1.0.0",
        description="A test plugin",
        author="Test Author",
        homepage="https://example.com",
        repository="https://github.com/test/plugin",
        license="MIT",
        dependencies=["dep1", "dep2"],
        tags=["test", "example"],
        install_url="https://example.com/plugin.zip",
        checksum="abc123",
    )


def test_plugin_metadata_to_dict(sample_metadata):
    """Test PluginMetadata to_dict conversion."""
    data = sample_metadata.to_dict()
    assert data["name"] == "test-plugin"
    assert data["version"] == "1.0.0"
    assert data["description"] == "A test plugin"
    assert data["author"] == "Test Author"
    assert data["dependencies"] == ["dep1", "dep2"]
    assert data["tags"] == ["test", "example"]


def test_plugin_metadata_from_dict():
    """Test PluginMetadata from_dict conversion."""
    data = {
        "name": "test-plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "author": "Test Author",
        "homepage": "https://example.com",
        "repository": "https://github.com/test/plugin",
        "license": "MIT",
        "dependencies": ["dep1"],
        "tags": ["test"],
        "install_url": "https://example.com/plugin.zip",
        "checksum": "abc123",
    }
    metadata = PluginMetadata.from_dict(data)
    assert metadata.name == "test-plugin"
    assert metadata.version == "1.0.0"
    assert metadata.author == "Test Author"


def test_registry_initialization(temp_registry_file):
    """Test registry initialization."""
    registry = PluginRegistry(temp_registry_file)
    assert registry.registry_path == Path(temp_registry_file)
    assert registry.plugins == {}


def test_register_plugin(registry, sample_metadata):
    """Test registering a plugin."""
    registry.register(sample_metadata)
    assert "test-plugin" in registry.plugins
    assert registry.plugins["test-plugin"].version == "1.0.0"


def test_unregister_plugin(registry, sample_metadata):
    """Test unregistering a plugin."""
    registry.register(sample_metadata)
    assert "test-plugin" in registry.plugins

    result = registry.unregister("test-plugin")
    assert result is True
    assert "test-plugin" not in registry.plugins


def test_unregister_nonexistent_plugin(registry):
    """Test unregistering a nonexistent plugin."""
    result = registry.unregister("nonexistent")
    assert result is False


def test_get_plugin(registry, sample_metadata):
    """Test getting plugin metadata."""
    registry.register(sample_metadata)
    metadata = registry.get("test-plugin")
    assert metadata is not None
    assert metadata.name == "test-plugin"


def test_get_nonexistent_plugin(registry):
    """Test getting nonexistent plugin."""
    metadata = registry.get("nonexistent")
    assert metadata is None


def test_list_all_plugins(registry):
    """Test listing all plugins."""
    metadata1 = PluginMetadata(name="plugin1", version="1.0.0", description="Plugin 1")
    metadata2 = PluginMetadata(name="plugin2", version="2.0.0", description="Plugin 2")

    registry.register(metadata1)
    registry.register(metadata2)

    plugins = registry.list_all()
    assert len(plugins) == 2
    assert any(p.name == "plugin1" for p in plugins)
    assert any(p.name == "plugin2" for p in plugins)


def test_search_by_query(registry):
    """Test searching plugins by query."""
    metadata1 = PluginMetadata(name="image-processor", version="1.0.0", description="Process images")
    metadata2 = PluginMetadata(name="video-editor", version="1.0.0", description="Edit videos")
    metadata3 = PluginMetadata(name="audio-processor", version="1.0.0", description="Process audio")

    registry.register(metadata1)
    registry.register(metadata2)
    registry.register(metadata3)

    # Search by name
    results = registry.search(query="processor")
    assert len(results) == 2
    assert any(p.name == "image-processor" for p in results)
    assert any(p.name == "audio-processor" for p in results)

    # Search by description
    results = registry.search(query="edit")
    assert len(results) == 1
    assert results[0].name == "video-editor"


def test_search_by_tags(registry):
    """Test searching plugins by tags."""
    metadata1 = PluginMetadata(
        name="plugin1", version="1.0.0", description="Plugin 1", tags=["media", "image"]
    )
    metadata2 = PluginMetadata(
        name="plugin2", version="1.0.0", description="Plugin 2", tags=["media", "video"]
    )
    metadata3 = PluginMetadata(
        name="plugin3", version="1.0.0", description="Plugin 3", tags=["utility"]
    )

    registry.register(metadata1)
    registry.register(metadata2)
    registry.register(metadata3)

    results = registry.search(tags=["media"])
    assert len(results) == 2

    results = registry.search(tags=["image"])
    assert len(results) == 1
    assert results[0].name == "plugin1"


def test_search_by_author(registry):
    """Test searching plugins by author."""
    metadata1 = PluginMetadata(
        name="plugin1", version="1.0.0", description="Plugin 1", author="John Doe"
    )
    metadata2 = PluginMetadata(
        name="plugin2", version="1.0.0", description="Plugin 2", author="Jane Smith"
    )
    metadata3 = PluginMetadata(
        name="plugin3", version="1.0.0", description="Plugin 3", author="John Smith"
    )

    registry.register(metadata1)
    registry.register(metadata2)
    registry.register(metadata3)

    results = registry.search(author="john")
    assert len(results) == 2


def test_search_combined_filters(registry):
    """Test searching with combined filters."""
    metadata1 = PluginMetadata(
        name="image-processor",
        version="1.0.0",
        description="Process images",
        author="John Doe",
        tags=["media", "image"],
    )
    metadata2 = PluginMetadata(
        name="video-processor",
        version="1.0.0",
        description="Process videos",
        author="John Doe",
        tags=["media", "video"],
    )

    registry.register(metadata1)
    registry.register(metadata2)

    results = registry.search(query="processor", tags=["image"], author="john")
    assert len(results) == 1
    assert results[0].name == "image-processor"


def test_sync_from_remote_merge(registry, sample_metadata):
    """Test syncing from remote with merge."""
    # Register local plugin
    registry.register(sample_metadata)

    # Mock remote data
    remote_data = {
        "remote-plugin": {
            "name": "remote-plugin",
            "version": "1.0.0",
            "description": "Remote plugin",
            "author": "",
            "homepage": "",
            "repository": "",
            "license": "",
            "dependencies": [],
            "tags": [],
            "install_url": None,
            "checksum": None,
        }
    }

    mock_response = Mock()
    mock_response.json.return_value = remote_data
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        success, message = registry.sync_from_remote("https://example.com/registry.json", merge=True)

    assert success is True
    assert "test-plugin" in registry.plugins  # Local plugin preserved
    assert "remote-plugin" in registry.plugins  # Remote plugin added


def test_sync_from_remote_replace(registry, sample_metadata):
    """Test syncing from remote with replace."""
    # Register local plugin
    registry.register(sample_metadata)

    # Mock remote data
    remote_data = {
        "remote-plugin": {
            "name": "remote-plugin",
            "version": "1.0.0",
            "description": "Remote plugin",
            "author": "",
            "homepage": "",
            "repository": "",
            "license": "",
            "dependencies": [],
            "tags": [],
            "install_url": None,
            "checksum": None,
        }
    }

    mock_response = Mock()
    mock_response.json.return_value = remote_data
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        success, message = registry.sync_from_remote("https://example.com/registry.json", merge=False)

    assert success is True
    assert "test-plugin" not in registry.plugins  # Local plugin removed
    assert "remote-plugin" in registry.plugins  # Remote plugin added


def test_sync_from_remote_network_error(registry):
    """Test syncing from remote with network error."""
    with patch("requests.get", side_effect=requests.RequestException("Network error")):
        success, message = registry.sync_from_remote("https://example.com/registry.json")

    assert success is False
    assert "Failed to sync" in message


def test_sync_from_remote_invalid_json(registry):
    """Test syncing from remote with invalid JSON."""
    mock_response = Mock()
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        success, message = registry.sync_from_remote("https://example.com/registry.json")

    assert success is False
    assert "Invalid remote registry format" in message


def test_check_updates(registry):
    """Test checking for updates."""
    # Register local plugin with old version
    metadata = PluginMetadata(name="test-plugin", version="1.0.0", description="Test plugin")
    registry.register(metadata)

    # Mock remote data with newer version
    remote_data = {
        "test-plugin": {
            "name": "test-plugin",
            "version": "2.0.0",
            "description": "Test plugin",
            "author": "",
            "homepage": "",
            "repository": "",
            "license": "",
            "dependencies": [],
            "tags": [],
            "install_url": None,
            "checksum": None,
        }
    }

    mock_response = Mock()
    mock_response.json.return_value = remote_data
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        updates = registry.check_updates("https://example.com/registry.json")

    assert len(updates) == 1
    assert updates[0] == ("test-plugin", "1.0.0", "2.0.0")


def test_check_updates_no_updates(registry):
    """Test checking for updates when no updates available."""
    # Register local plugin with current version
    metadata = PluginMetadata(name="test-plugin", version="2.0.0", description="Test plugin")
    registry.register(metadata)

    # Mock remote data with same version
    remote_data = {
        "test-plugin": {
            "name": "test-plugin",
            "version": "2.0.0",
            "description": "Test plugin",
            "author": "",
            "homepage": "",
            "repository": "",
            "license": "",
            "dependencies": [],
            "tags": [],
            "install_url": None,
            "checksum": None,
        }
    }

    mock_response = Mock()
    mock_response.json.return_value = remote_data
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        updates = registry.check_updates("https://example.com/registry.json")

    assert len(updates) == 0


def test_check_updates_network_error(registry):
    """Test checking for updates with network error."""
    with patch("requests.get", side_effect=requests.RequestException("Network error")):
        updates = registry.check_updates("https://example.com/registry.json")

    assert len(updates) == 0


def test_is_newer_version(registry):
    """Test version comparison."""
    assert registry._is_newer_version("2.0.0", "1.0.0") is True
    assert registry._is_newer_version("1.1.0", "1.0.0") is True
    assert registry._is_newer_version("1.0.1", "1.0.0") is True
    assert registry._is_newer_version("1.0.0", "1.0.0") is False
    assert registry._is_newer_version("1.0.0", "2.0.0") is False
    assert registry._is_newer_version("1.0", "1.0.0") is False  # Padded with zeros


def test_is_newer_version_invalid(registry):
    """Test version comparison with invalid versions."""
    assert registry._is_newer_version("invalid", "1.0.0") is False
    assert registry._is_newer_version("1.0.0", "invalid") is False


def test_export_to_file(registry, sample_metadata):
    """Test exporting registry to file."""
    registry.register(sample_metadata)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        export_path = f.name

    try:
        registry.export_to_file(export_path)

        with open(export_path, "r") as f:
            data = json.load(f)

        assert "test-plugin" in data
        assert data["test-plugin"]["version"] == "1.0.0"
    finally:
        os.remove(export_path)


def test_import_from_file_merge(registry, sample_metadata):
    """Test importing registry from file with merge."""
    # Register local plugin
    registry.register(sample_metadata)

    # Create import file
    import_data = {
        "imported-plugin": {
            "name": "imported-plugin",
            "version": "1.0.0",
            "description": "Imported plugin",
            "author": "",
            "homepage": "",
            "repository": "",
            "license": "",
            "dependencies": [],
            "tags": [],
            "install_url": None,
            "checksum": None,
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(import_data, f)
        import_path = f.name

    try:
        success, message = registry.import_from_file(import_path, merge=True)

        assert success is True
        assert "test-plugin" in registry.plugins  # Local plugin preserved
        assert "imported-plugin" in registry.plugins  # Imported plugin added
    finally:
        os.remove(import_path)


def test_import_from_file_replace(registry, sample_metadata):
    """Test importing registry from file with replace."""
    # Register local plugin
    registry.register(sample_metadata)

    # Create import file
    import_data = {
        "imported-plugin": {
            "name": "imported-plugin",
            "version": "1.0.0",
            "description": "Imported plugin",
            "author": "",
            "homepage": "",
            "repository": "",
            "license": "",
            "dependencies": [],
            "tags": [],
            "install_url": None,
            "checksum": None,
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(import_data, f)
        import_path = f.name

    try:
        success, message = registry.import_from_file(import_path, merge=False)

        assert success is True
        assert "test-plugin" not in registry.plugins  # Local plugin removed
        assert "imported-plugin" in registry.plugins  # Imported plugin added
    finally:
        os.remove(import_path)


def test_import_from_file_not_found(registry):
    """Test importing from nonexistent file."""
    success, message = registry.import_from_file("/nonexistent/file.json")
    assert success is False
    assert "File not found" in message


def test_import_from_file_invalid_json(registry):
    """Test importing from file with invalid JSON."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("invalid json")
        import_path = f.name

    try:
        success, message = registry.import_from_file(import_path)
        assert success is False
        assert "Invalid registry format" in message
    finally:
        os.remove(import_path)


def test_get_stats(registry):
    """Test getting registry statistics."""
    metadata1 = PluginMetadata(
        name="plugin1", version="1.0.0", description="Plugin 1", author="Author A", tags=["tag1", "tag2"]
    )
    metadata2 = PluginMetadata(
        name="plugin2", version="1.0.0", description="Plugin 2", author="Author A", tags=["tag1"]
    )
    metadata3 = PluginMetadata(
        name="plugin3", version="1.0.0", description="Plugin 3", author="Author B", tags=["tag2"]
    )

    registry.register(metadata1)
    registry.register(metadata2)
    registry.register(metadata3)

    stats = registry.get_stats()
    assert stats["total_plugins"] == 3
    assert stats["plugins_by_author"]["Author A"] == 2
    assert stats["plugins_by_author"]["Author B"] == 1
    assert stats["plugins_by_tag"]["tag1"] == 2
    assert stats["plugins_by_tag"]["tag2"] == 2


def test_get_stats_unknown_author(registry):
    """Test getting stats with unknown author."""
    metadata = PluginMetadata(name="plugin1", version="1.0.0", description="Plugin 1", author="")
    registry.register(metadata)

    stats = registry.get_stats()
    assert stats["plugins_by_author"]["Unknown"] == 1


def test_registry_persistence(temp_registry_file, sample_metadata):
    """Test that registry persists across instances."""
    # Create first registry and register plugin
    registry1 = PluginRegistry(temp_registry_file)
    registry1.register(sample_metadata)

    # Create second registry with same file
    registry2 = PluginRegistry(temp_registry_file)
    assert "test-plugin" in registry2.plugins
    assert registry2.plugins["test-plugin"].version == "1.0.0"


def test_registry_corrupted_file(temp_registry_file):
    """Test loading registry from corrupted file."""
    # Write corrupted JSON
    with open(temp_registry_file, "w") as f:
        f.write("invalid json")

    # Should start with empty registry
    registry = PluginRegistry(temp_registry_file)
    assert registry.plugins == {}


def test_sync_from_remote_update_newer_version(registry):
    """Test syncing updates plugin with newer version."""
    # Register local plugin with old version
    metadata = PluginMetadata(name="test-plugin", version="1.0.0", description="Test plugin")
    registry.register(metadata)

    # Mock remote data with newer version
    remote_data = {
        "test-plugin": {
            "name": "test-plugin",
            "version": "2.0.0",
            "description": "Updated plugin",
            "author": "",
            "homepage": "",
            "repository": "",
            "license": "",
            "dependencies": [],
            "tags": [],
            "install_url": None,
            "checksum": None,
        }
    }

    mock_response = Mock()
    mock_response.json.return_value = remote_data
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        success, message = registry.sync_from_remote("https://example.com/registry.json", merge=True)

    assert success is True
    assert registry.plugins["test-plugin"].version == "2.0.0"
    assert registry.plugins["test-plugin"].description == "Updated plugin"


def test_sync_from_remote_skip_older_version(registry):
    """Test syncing skips plugin with older version."""
    # Register local plugin with newer version
    metadata = PluginMetadata(name="test-plugin", version="2.0.0", description="Test plugin")
    registry.register(metadata)

    # Mock remote data with older version
    remote_data = {
        "test-plugin": {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Old plugin",
            "author": "",
            "homepage": "",
            "repository": "",
            "license": "",
            "dependencies": [],
            "tags": [],
            "install_url": None,
            "checksum": None,
        }
    }

    mock_response = Mock()
    mock_response.json.return_value = remote_data
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        success, message = registry.sync_from_remote("https://example.com/registry.json", merge=True)

    assert success is True
    assert registry.plugins["test-plugin"].version == "2.0.0"  # Version not downgraded
    assert registry.plugins["test-plugin"].description == "Test plugin"  # Description not changed


def test_sync_from_remote_invalid_plugin_data(registry):
    """Test syncing with invalid plugin data in remote."""
    # Mock remote data with invalid plugin
    remote_data = {
        "valid-plugin": {
            "name": "valid-plugin",
            "version": "1.0.0",
            "description": "Valid plugin",
            "author": "",
            "homepage": "",
            "repository": "",
            "license": "",
            "dependencies": [],
            "tags": [],
            "install_url": None,
            "checksum": None,
        },
        "invalid-plugin": {
            # Missing required fields
            "version": "1.0.0",
        },
    }

    mock_response = Mock()
    mock_response.json.return_value = remote_data
    mock_response.raise_for_status = Mock()

    with patch("requests.get", return_value=mock_response):
        success, message = registry.sync_from_remote("https://example.com/registry.json", merge=True)

    assert success is True
    assert "valid-plugin" in registry.plugins
    assert "invalid-plugin" not in registry.plugins  # Invalid plugin skipped


def test_import_from_file_invalid_plugin_data(registry):
    """Test importing with invalid plugin data."""
    import_data = {
        "valid-plugin": {
            "name": "valid-plugin",
            "version": "1.0.0",
            "description": "Valid plugin",
            "author": "",
            "homepage": "",
            "repository": "",
            "license": "",
            "dependencies": [],
            "tags": [],
            "install_url": None,
            "checksum": None,
        },
        "invalid-plugin": {
            # Missing required fields
            "version": "1.0.0",
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(import_data, f)
        import_path = f.name

    try:
        success, message = registry.import_from_file(import_path, merge=True)

        assert success is True
        assert "valid-plugin" in registry.plugins
        assert "invalid-plugin" not in registry.plugins  # Invalid plugin skipped
    finally:
        os.remove(import_path)
