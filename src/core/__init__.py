"""Core module initialization"""

from src.core.plugin_manager import PluginManager, Plugin
from src.core.agent_manager import AgentManager, Agent
from src.core.config_manager import ConfigManager

__all__ = [
    "PluginManager",
    "Plugin",
    "AgentManager",
    "Agent",
    "ConfigManager",
]
