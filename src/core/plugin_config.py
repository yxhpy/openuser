"""
Plugin Configuration Schema

This module provides configuration schema support for plugins.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

import yaml


class ConfigFieldType(Enum):
    """Configuration field types"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"


@dataclass
class ConfigField:
    """Configuration field definition"""

    name: str
    field_type: ConfigFieldType
    required: bool = False
    default: Any = None
    description: str = ""
    validator: Optional[Callable[[Any], bool]] = None

    def validate(self, value: Any) -> bool:
        """
        Validate field value

        Args:
            value: Value to validate

        Returns:
            True if valid, False otherwise
        """
        # Check type
        type_map: Dict[ConfigFieldType, Union[Type[Any], tuple[Type[Any], ...]]] = {
            ConfigFieldType.STRING: str,
            ConfigFieldType.INTEGER: int,
            ConfigFieldType.FLOAT: (int, float),
            ConfigFieldType.BOOLEAN: bool,
            ConfigFieldType.LIST: list,
            ConfigFieldType.DICT: dict,
        }

        expected_type = type_map[self.field_type]
        if not isinstance(value, expected_type):
            return False

        # Run custom validator if provided
        if self.validator and not self.validator(value):
            return False

        return True


@dataclass
class PluginConfigSchema:
    """Plugin configuration schema"""

    fields: List[ConfigField] = field(default_factory=list)

    def add_field(self, config_field: ConfigField) -> None:
        """Add a field to the schema"""
        self.fields.append(config_field)

    def validate(self, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate configuration against schema

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        for field in self.fields:
            if field.required and field.name not in config:
                errors.append(f"Required field '{field.name}' is missing")
                continue

            # Skip validation if field not present and not required
            if field.name not in config:
                continue

            # Validate field value
            value = config[field.name]
            if not field.validate(value):
                errors.append(f"Field '{field.name}' has invalid value: {value}")

        return len(errors) == 0, errors

    def get_defaults(self) -> Dict[str, Any]:
        """
        Get default configuration values

        Returns:
            Dictionary of default values
        """
        defaults = {}
        for field in self.fields:
            if field.default is not None:
                defaults[field.name] = field.default
        return defaults


class PluginConfig:
    """
    Plugin configuration manager

    Handles loading, validation, and hot-reload of plugin configurations.
    """

    def __init__(
        self,
        plugin_name: str,
        schema: Optional[PluginConfigSchema] = None,
        config_dir: str = "config/plugins",
    ) -> None:
        self.plugin_name = plugin_name
        self.schema = schema or PluginConfigSchema()
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file"""
        # Try JSON first
        json_path = self.config_dir / f"{self.plugin_name}.json"
        if json_path.exists():
            with open(json_path, "r") as f:
                self.config = json.load(f)
            return

        # Try YAML
        yaml_path = self.config_dir / f"{self.plugin_name}.yaml"
        if yaml_path.exists():
            with open(yaml_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
            return

        # Use defaults if no config file found
        self.config = self.schema.get_defaults()

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate current configuration

        Returns:
            Tuple of (is_valid, error_messages)
        """
        return self.schema.validate(self.config)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
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

    def reload(self) -> bool:
        """
        Hot-reload configuration from file

        Returns:
            True if successful, False otherwise
        """
        try:
            self._load_config()
            is_valid, errors = self.validate()
            if not is_valid:
                raise ValueError(f"Invalid configuration: {errors}")
            return True
        except Exception:
            return False

    def save(self, format: str = "json") -> bool:
        """
        Save configuration to file

        Args:
            format: File format ("json" or "yaml")

        Returns:
            True if successful, False otherwise
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)

            if format == "json":
                path = self.config_dir / f"{self.plugin_name}.json"
                with open(path, "w") as f:
                    json.dump(self.config, f, indent=2)
            elif format == "yaml":
                path = self.config_dir / f"{self.plugin_name}.yaml"
                with open(path, "w") as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported format: {format}")

            return True
        except Exception:
            return False
