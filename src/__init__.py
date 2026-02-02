"""OpenUser - Intelligent Digital Human System"""

__version__ = "0.1.0"
__author__ = "OpenUser Team"
__license__ = "MIT"

from src.core.plugin_manager import PluginManager
from src.core.agent_manager import AgentManager
from src.core.config_manager import ConfigManager

__all__ = [
    "PluginManager",
    "AgentManager",
    "ConfigManager",
]
