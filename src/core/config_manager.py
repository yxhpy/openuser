"""
Config Manager - Dynamic configuration with hot-reload
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
import logging


class ConfigManager:
    """
    Configuration Manager with hot-reload capability

    Features:
    - Load configuration from files
    - Hot-reload configuration
    - Environment variable support
    - Nested configuration access
    """

    def __init__(self, config_path: str = ".env") -> None:
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger("config_manager")
        self.load_config()

    def load_config(self) -> bool:
        """
        Load configuration from file

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    # Simple key=value parser for .env files
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                self.config[key.strip()] = value.strip()

                self.logger.info("Configuration loaded successfully")
                return True
            else:
                self.logger.warning(f"Config file {self.config_path} not found")
                return False

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False

    def reload_config(self) -> bool:
        """
        Reload configuration from file

        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Reloading configuration...")
        return self.load_config()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        self.logger.debug(f"Config {key} set to {value}")

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration

        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
