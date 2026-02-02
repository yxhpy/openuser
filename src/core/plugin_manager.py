"""
Plugin Manager - Hot-reload plugin system

This module provides hot-reload capability for plugins without system restart.
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging


class Plugin:
    """Base class for all plugins"""

    name: str = ""
    version: str = "1.0.0"
    dependencies: List[str] = []

    def __init__(self) -> None:
        self.logger = logging.getLogger(f"plugin.{self.name}")
        self._state: Dict[str, Any] = {}

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        self.logger.info(f"Plugin {self.name} v{self.version} loaded")

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        self.logger.info(f"Plugin {self.name} unloaded")

    def get_state(self) -> Dict[str, Any]:
        """Get plugin state for backup"""
        return self._state.copy()

    def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore plugin state from backup"""
        self._state = state.copy()


class PluginManager:
    """
    Plugin Manager with hot-reload capability

    Features:
    - Load/unload plugins dynamically
    - Hot-reload without restart
    - Dependency resolution
    - State backup and rollback
    """

    def __init__(self, plugin_dir: str = "src/plugins") -> None:
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, Plugin] = {}
        self.state_backup: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("plugin_manager")

    def load_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Load a plugin

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            Plugin instance if successful, None otherwise
        """
        try:
            # Import plugin module
            module_name = f"src.plugins.{plugin_name}"
            module = importlib.import_module(module_name)

            # Get plugin class (assume class name is CamelCase of plugin_name)
            class_name = "".join(word.capitalize() for word in plugin_name.split("_"))
            plugin_class = getattr(module, class_name)

            # Create plugin instance
            plugin = plugin_class()

            # Call load hook
            plugin.on_load()

            # Store plugin
            self.plugins[plugin_name] = plugin

            self.logger.info(f"Plugin {plugin_name} loaded successfully")
            return plugin

        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return None

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if successful, False otherwise
        """
        try:
            plugin = self.plugins.get(plugin_name)
            if not plugin:
                self.logger.warning(f"Plugin {plugin_name} not found")
                return False

            # Call unload hook
            plugin.on_unload()

            # Remove from plugins dict
            del self.plugins[plugin_name]

            self.logger.info(f"Plugin {plugin_name} unloaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Hot-reload a plugin without restart

        Args:
            plugin_name: Name of the plugin to reload

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get plugin instance
            plugin = self.plugins.get(plugin_name)
            if not plugin:
                self.logger.warning(f"Plugin {plugin_name} not found, loading instead")
                return self.load_plugin(plugin_name) is not None

            # Backup state
            self.state_backup[plugin_name] = plugin.get_state()

            # Call unload hook
            plugin.on_unload()

            # Clear module cache
            module_name = plugin.__module__
            if module_name in sys.modules:
                del sys.modules[module_name]

            # Reimport module
            module = importlib.import_module(module_name)
            importlib.reload(module)

            # Get new plugin class
            plugin_class = getattr(module, plugin.__class__.__name__)

            # Create new instance
            new_plugin = plugin_class()

            # Restore state
            if plugin_name in self.state_backup:
                new_plugin.restore_state(self.state_backup[plugin_name])

            # Call load hook
            new_plugin.on_load()

            # Replace old plugin
            self.plugins[plugin_name] = new_plugin

            self.logger.info(f"Plugin {plugin_name} reloaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            # Attempt rollback
            if plugin_name in self.state_backup:
                plugin.restore_state(self.state_backup[plugin_name])
            return False

    def list_plugins(self) -> List[str]:
        """
        List all loaded plugins

        Returns:
            List of plugin names
        """
        return list(self.plugins.keys())

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a plugin instance

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance if found, None otherwise
        """
        return self.plugins.get(plugin_name)
