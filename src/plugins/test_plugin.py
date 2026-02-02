"""Test plugin for testing plugin manager functionality"""

from src.core.plugin_manager import Plugin


class TestPlugin(Plugin):
    """A simple test plugin"""

    name = "test_plugin"
    version = "1.0.0"
    dependencies = []

    def __init__(self) -> None:
        super().__init__()
        self.loaded = False
        self.unloaded = False

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        super().on_load()
        self.loaded = True

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        super().on_unload()
        self.unloaded = True
        self.loaded = False
