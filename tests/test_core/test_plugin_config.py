"""Tests for plugin configuration system"""

import pytest
import json
import yaml
from pathlib import Path
from src.core.plugin_config import (
    ConfigField,
    ConfigFieldType,
    PluginConfigSchema,
    PluginConfig,
)


class TestConfigField:
    """Test ConfigField class"""

    def test_string_field_validation(self):
        """Test string field validation"""
        field = ConfigField(
            name="test_field",
            field_type=ConfigFieldType.STRING,
            required=True
        )

        assert field.validate("test") is True
        assert field.validate(123) is False
        assert field.validate(True) is False

    def test_integer_field_validation(self):
        """Test integer field validation"""
        field = ConfigField(
            name="test_field",
            field_type=ConfigFieldType.INTEGER,
            required=True
        )

        assert field.validate(123) is True
        assert field.validate("test") is False
        assert field.validate(12.5) is False

    def test_float_field_validation(self):
        """Test float field validation"""
        field = ConfigField(
            name="test_field",
            field_type=ConfigFieldType.FLOAT,
            required=True
        )

        assert field.validate(12.5) is True
        assert field.validate(123) is True  # int is acceptable for float
        assert field.validate("test") is False

    def test_boolean_field_validation(self):
        """Test boolean field validation"""
        field = ConfigField(
            name="test_field",
            field_type=ConfigFieldType.BOOLEAN,
            required=True
        )

        assert field.validate(True) is True
        assert field.validate(False) is True
        assert field.validate(1) is False
        assert field.validate("true") is False

    def test_list_field_validation(self):
        """Test list field validation"""
        field = ConfigField(
            name="test_field",
            field_type=ConfigFieldType.LIST,
            required=True
        )

        assert field.validate([1, 2, 3]) is True
        assert field.validate([]) is True
        assert field.validate("test") is False
        assert field.validate({}) is False

    def test_dict_field_validation(self):
        """Test dict field validation"""
        field = ConfigField(
            name="test_field",
            field_type=ConfigFieldType.DICT,
            required=True
        )

        assert field.validate({"key": "value"}) is True
        assert field.validate({}) is True
        assert field.validate([]) is False
        assert field.validate("test") is False

    def test_custom_validator(self):
        """Test custom validator function"""
        def positive_validator(value):
            return value > 0

        field = ConfigField(
            name="test_field",
            field_type=ConfigFieldType.INTEGER,
            validator=positive_validator
        )

        assert field.validate(10) is True
        assert field.validate(-5) is False
        assert field.validate(0) is False


class TestPluginConfigSchema:
    """Test PluginConfigSchema class"""

    def test_add_field(self):
        """Test adding fields to schema"""
        schema = PluginConfigSchema()
        field = ConfigField(
            name="test_field",
            field_type=ConfigFieldType.STRING
        )

        schema.add_field(field)
        assert len(schema.fields) == 1
        assert schema.fields[0] == field

    def test_validate_required_fields(self):
        """Test validation of required fields"""
        schema = PluginConfigSchema()
        schema.add_field(ConfigField(
            name="required_field",
            field_type=ConfigFieldType.STRING,
            required=True
        ))

        # Missing required field
        is_valid, errors = schema.validate({})
        assert is_valid is False
        assert len(errors) == 1
        assert "required_field" in errors[0]

        # Required field present
        is_valid, errors = schema.validate({"required_field": "value"})
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_field_types(self):
        """Test validation of field types"""
        schema = PluginConfigSchema()
        schema.add_field(ConfigField(
            name="string_field",
            field_type=ConfigFieldType.STRING
        ))
        schema.add_field(ConfigField(
            name="int_field",
            field_type=ConfigFieldType.INTEGER
        ))

        # Valid types
        is_valid, errors = schema.validate({
            "string_field": "test",
            "int_field": 123
        })
        assert is_valid is True

        # Invalid types
        is_valid, errors = schema.validate({
            "string_field": 123,
            "int_field": "test"
        })
        assert is_valid is False
        assert len(errors) == 2

    def test_get_defaults(self):
        """Test getting default values"""
        schema = PluginConfigSchema()
        schema.add_field(ConfigField(
            name="field1",
            field_type=ConfigFieldType.STRING,
            default="default1"
        ))
        schema.add_field(ConfigField(
            name="field2",
            field_type=ConfigFieldType.INTEGER,
            default=42
        ))
        schema.add_field(ConfigField(
            name="field3",
            field_type=ConfigFieldType.STRING
        ))

        defaults = schema.get_defaults()
        assert defaults == {"field1": "default1", "field2": 42}


class TestPluginConfig:
    """Test PluginConfig class"""

    def test_init_with_defaults(self, tmp_path):
        """Test initialization with default values"""
        schema = PluginConfigSchema()
        schema.add_field(ConfigField(
            name="field1",
            field_type=ConfigFieldType.STRING,
            default="default_value"
        ))

        config = PluginConfig(
            plugin_name="test_plugin",
            schema=schema,
            config_dir=str(tmp_path)
        )

        assert config.get("field1") == "default_value"

    def test_load_json_config(self, tmp_path):
        """Test loading configuration from JSON file"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        config_data = {"field1": "value1", "field2": 123}
        config_file = config_dir / "test_plugin.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = PluginConfig(
            plugin_name="test_plugin",
            config_dir=str(config_dir)
        )

        assert config.get("field1") == "value1"
        assert config.get("field2") == 123

    def test_load_yaml_config(self, tmp_path):
        """Test loading configuration from YAML file"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        config_data = {"field1": "value1", "field2": 123}
        config_file = config_dir / "test_plugin.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = PluginConfig(
            plugin_name="test_plugin",
            config_dir=str(config_dir)
        )

        assert config.get("field1") == "value1"
        assert config.get("field2") == 123

    def test_get_with_default(self, tmp_path):
        """Test getting value with default"""
        config = PluginConfig(
            plugin_name="test_plugin",
            config_dir=str(tmp_path)
        )

        assert config.get("nonexistent", "default") == "default"

    def test_set_value(self, tmp_path):
        """Test setting configuration value"""
        config = PluginConfig(
            plugin_name="test_plugin",
            config_dir=str(tmp_path)
        )

        config.set("field1", "value1")
        assert config.get("field1") == "value1"

    def test_save_json(self, tmp_path):
        """Test saving configuration to JSON file"""
        config = PluginConfig(
            plugin_name="test_plugin",
            config_dir=str(tmp_path)
        )

        config.set("field1", "value1")
        config.set("field2", 123)

        assert config.save(format="json") is True

        config_file = tmp_path / "test_plugin.json"
        assert config_file.exists()

        with open(config_file, "r") as f:
            saved_data = json.load(f)

        assert saved_data == {"field1": "value1", "field2": 123}

    def test_save_yaml(self, tmp_path):
        """Test saving configuration to YAML file"""
        config = PluginConfig(
            plugin_name="test_plugin",
            config_dir=str(tmp_path)
        )

        config.set("field1", "value1")
        config.set("field2", 123)

        assert config.save(format="yaml") is True

        config_file = tmp_path / "test_plugin.yaml"
        assert config_file.exists()

        with open(config_file, "r") as f:
            saved_data = yaml.safe_load(f)

        assert saved_data == {"field1": "value1", "field2": 123}

    def test_reload_config(self, tmp_path):
        """Test hot-reloading configuration"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Initial config
        config_data = {"field1": "value1"}
        config_file = config_dir / "test_plugin.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = PluginConfig(
            plugin_name="test_plugin",
            config_dir=str(config_dir)
        )

        assert config.get("field1") == "value1"

        # Update config file
        config_data = {"field1": "value2", "field2": 123}
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Reload
        assert config.reload() is True
        assert config.get("field1") == "value2"
        assert config.get("field2") == 123

    def test_validate(self, tmp_path):
        """Test configuration validation"""
        schema = PluginConfigSchema()
        schema.add_field(ConfigField(
            name="required_field",
            field_type=ConfigFieldType.STRING,
            required=True
        ))

        config = PluginConfig(
            plugin_name="test_plugin",
            schema=schema,
            config_dir=str(tmp_path)
        )

        # Invalid - missing required field
        is_valid, errors = config.validate()
        assert is_valid is False
        assert len(errors) > 0

        # Valid - add required field
        config.set("required_field", "value")
        is_valid, errors = config.validate()
        assert is_valid is True
        assert len(errors) == 0

    def test_reload_invalid_config(self, tmp_path):
        """Test reloading invalid configuration"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        schema = PluginConfigSchema()
        schema.add_field(ConfigField(
            name="required_field",
            field_type=ConfigFieldType.STRING,
            required=True
        ))

        # Create invalid config file (missing required field)
        config_file = config_dir / "test_plugin.json"
        with open(config_file, "w") as f:
            json.dump({}, f)

        config = PluginConfig(
            plugin_name="test_plugin",
            schema=schema,
            config_dir=str(config_dir)
        )

        # Reload should fail due to validation error
        assert config.reload() is False

    def test_save_unsupported_format(self, tmp_path):
        """Test saving with unsupported format"""
        config = PluginConfig(
            plugin_name="test_plugin",
            config_dir=str(tmp_path)
        )

        config.set("field1", "value1")

        # Should fail with unsupported format
        assert config.save(format="xml") is False

    def test_optional_field_not_present(self, tmp_path):
        """Test validation with optional field not present"""
        schema = PluginConfigSchema()
        schema.add_field(ConfigField(
            name="optional_field",
            field_type=ConfigFieldType.STRING,
            required=False
        ))

        config = PluginConfig(
            plugin_name="test_plugin",
            schema=schema,
            config_dir=str(tmp_path)
        )

        # Should be valid even without optional field
        is_valid, errors = config.validate()
        assert is_valid is True
        assert len(errors) == 0



