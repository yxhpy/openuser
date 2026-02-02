"""Tests for Plugin Manager"""

import pytest
from src.core.plugin_manager import PluginManager, Plugin


class TestPlugin(Plugin):
    """Test plugin for testing"""

    name = "test-plugin"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.loaded = False

    def on_load(self) -> None:
        super().on_load()
        self.loaded = True

    def on_unload(self) -> None:
        super().on_unload()
        self.loaded = False


def test_plugin_manager_init() -> None:
    """Test PluginManager initialization"""
    pm = PluginManager()
    assert pm is not None
    assert pm.plugins == {}
    assert pm.state_backup == {}


def test_plugin_base_class() -> None:
    """Test Plugin base class"""
    plugin = TestPlugin()
    assert plugin.name == "test-plugin"
    assert plugin.version == "1.0.0"
    assert plugin.dependencies == []


def test_plugin_state_management() -> None:
    """Test plugin state backup and restore"""
    plugin = TestPlugin()

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
    plugin = TestPlugin()
    pm.plugins["test-plugin"] = plugin

    assert pm.list_plugins() == ["test-plugin"]


def test_plugin_manager_get_plugin() -> None:
    """Test getting a plugin"""
    pm = PluginManager()

    # Add a plugin manually for testing
    plugin = TestPlugin()
    pm.plugins["test-plugin"] = plugin

    # Get existing plugin
    retrieved = pm.get_plugin("test-plugin")
    assert retrieved is plugin

    # Get non-existing plugin
    assert pm.get_plugin("non-existing") is None
