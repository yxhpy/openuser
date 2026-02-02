"""Tests for Plugin Manager"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.plugin_manager import PluginManager, Plugin


class MockPlugin(Plugin):
    """Mock plugin for testing"""

    name = "mock-plugin"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.loaded = False
        self.unloaded = False

    def on_load(self) -> None:
        super().on_load()
        self.loaded = True

    def on_unload(self) -> None:
        super().on_unload()
        self.unloaded = True
        self.loaded = False


def test_plugin_manager_init() -> None:
    """Test PluginManager initialization"""
    pm = PluginManager()
    assert pm is not None
    assert pm.plugins == {}
    assert pm.state_backup == {}


def test_plugin_base_class() -> None:
    """Test Plugin base class"""
    plugin = MockPlugin()
    assert plugin.name == "mock-plugin"
    assert plugin.version == "1.0.0"
    assert plugin.dependencies == []


def test_plugin_lifecycle_hooks() -> None:
    """Test plugin on_load and on_unload hooks"""
    plugin = MockPlugin()
    assert plugin.loaded is False
    assert plugin.unloaded is False

    # Test on_load
    plugin.on_load()
    assert plugin.loaded is True

    # Test on_unload
    plugin.on_unload()
    assert plugin.unloaded is True
    assert plugin.loaded is False


def test_plugin_state_management() -> None:
    """Test plugin state backup and restore"""
    plugin = MockPlugin()

    # Set state
    plugin._state = {"key": "value"}

    # Get state
    state = plugin.get_state()
    assert state == {"key": "value"}

    # Modify original state
    plugin._state["key"] = "new_value"

    # Restore state
    plugin.restore_state(state)
    assert plugin._state == {"key": "value"}


def test_plugin_manager_list_plugins() -> None:
    """Test listing plugins"""
    pm = PluginManager()
    assert pm.list_plugins() == []

    # Add a plugin manually for testing
    plugin = MockPlugin()
    pm.plugins["mock-plugin"] = plugin

    assert pm.list_plugins() == ["mock-plugin"]


def test_plugin_manager_get_plugin() -> None:
    """Test getting a plugin"""
    pm = PluginManager()

    # Add a plugin manually for testing
    plugin = MockPlugin()
    pm.plugins["mock-plugin"] = plugin

    # Get existing plugin
    retrieved = pm.get_plugin("mock-plugin")
    assert retrieved is plugin

    # Get non-existing plugin
    assert pm.get_plugin("non-existing") is None


def test_load_plugin_success() -> None:
    """Test successful plugin loading"""
    pm = PluginManager()

    # Load the test plugin
    plugin = pm.load_plugin("test_plugin")

    assert plugin is not None
    assert plugin.name == "test_plugin"
    assert plugin.loaded is True
    assert "test_plugin" in pm.plugins


def test_load_plugin_failure_module_not_found() -> None:
    """Test plugin loading failure when module not found"""
    pm = PluginManager()

    # Try to load non-existent plugin
    plugin = pm.load_plugin("non_existent_plugin")

    assert plugin is None
    assert "non_existent_plugin" not in pm.plugins


def test_load_plugin_failure_class_not_found() -> None:
    """Test plugin loading failure when class not found"""
    pm = PluginManager()

    # Mock importlib to return a module without the expected class
    with patch("importlib.import_module") as mock_import:
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        # Remove the expected class attribute
        del mock_module.TestPlugin

        plugin = pm.load_plugin("test_plugin")

        assert plugin is None


def test_unload_plugin_success() -> None:
    """Test successful plugin unloading"""
    pm = PluginManager()

    # Load plugin first
    plugin = pm.load_plugin("test_plugin")
    assert plugin is not None
    assert "test_plugin" in pm.plugins

    # Unload plugin
    result = pm.unload_plugin("test_plugin")

    assert result is True
    assert plugin.unloaded is True
    assert "test_plugin" not in pm.plugins


def test_unload_plugin_not_found() -> None:
    """Test unloading non-existent plugin"""
    pm = PluginManager()

    # Try to unload non-existent plugin
    result = pm.unload_plugin("non_existent")

    assert result is False


def test_unload_plugin_with_exception() -> None:
    """Test unload plugin when on_unload raises exception"""
    pm = PluginManager()

    # Create a plugin that raises exception on unload
    plugin = MockPlugin()
    plugin.on_unload = MagicMock(side_effect=Exception("Unload error"))
    pm.plugins["mock-plugin"] = plugin

    # Try to unload - should handle exception and return False
    result = pm.unload_plugin("mock-plugin")

    assert result is False
    # Plugin should still be in plugins dict since unload failed
    assert "mock-plugin" in pm.plugins


def test_reload_plugin_success() -> None:
    """Test successful plugin reload"""
    pm = PluginManager()

    # Load plugin first
    plugin = pm.load_plugin("test_plugin")
    assert plugin is not None

    # Set some state
    plugin._state = {"counter": 1}

    # Reload plugin
    result = pm.reload_plugin("test_plugin")

    assert result is True
    assert "test_plugin" in pm.plugins

    # Get reloaded plugin
    reloaded = pm.get_plugin("test_plugin")
    assert reloaded is not None
    assert reloaded is not plugin  # Should be a new instance
    assert reloaded._state == {"counter": 1}  # State should be restored


def test_reload_plugin_not_found() -> None:
    """Test reload when plugin not found - should load instead"""
    pm = PluginManager()

    # Try to reload non-existent plugin - should load it instead
    result = pm.reload_plugin("test_plugin")

    assert result is True
    assert "test_plugin" in pm.plugins


def test_reload_plugin_with_exception() -> None:
    """Test reload plugin when reload fails"""
    pm = PluginManager()

    # Load plugin first
    plugin = pm.load_plugin("test_plugin")
    assert plugin is not None

    # Set some state
    original_state = {"key": "value"}
    plugin._state = original_state.copy()

    # Mock importlib.reload to raise exception
    with patch("importlib.reload", side_effect=Exception("Reload error")):
        result = pm.reload_plugin("test_plugin")

        assert result is False
        # Original plugin should still be there with restored state
        assert "test_plugin" in pm.plugins
        assert pm.get_plugin("test_plugin")._state == original_state


def test_plugin_manager_custom_plugin_dir() -> None:
    """Test PluginManager with custom plugin directory"""
    pm = PluginManager(plugin_dir="custom/plugins")
    assert str(pm.plugin_dir) == "custom/plugins"

