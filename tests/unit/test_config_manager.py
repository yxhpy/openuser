"""Tests for Config Manager"""

import pytest
import tempfile
from pathlib import Path
from src.core.config_manager import ConfigManager


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("# Test config file\n")
        f.write("KEY1=value1\n")
        f.write("KEY2=value2\n")
        f.write("KEY3=value with spaces\n")
        f.write("\n")  # Empty line
        f.write("# Comment line\n")
        f.write("KEY4=value4\n")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def empty_config_file():
    """Create an empty config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


def test_config_manager_init_with_existing_file(temp_config_file):
    """Test ConfigManager initialization with existing file"""
    cm = ConfigManager(config_path=temp_config_file)

    assert cm is not None
    assert cm.config_path == Path(temp_config_file)
    assert len(cm.config) > 0


def test_config_manager_init_with_nonexistent_file():
    """Test ConfigManager initialization with non-existent file"""
    cm = ConfigManager(config_path="/nonexistent/path/.env")

    assert cm is not None
    assert cm.config == {}


def test_config_manager_load_config_success(temp_config_file):
    """Test successful config loading"""
    cm = ConfigManager(config_path=temp_config_file)

    assert cm.config["KEY1"] == "value1"
    assert cm.config["KEY2"] == "value2"
    assert cm.config["KEY3"] == "value with spaces"
    assert cm.config["KEY4"] == "value4"


def test_config_manager_load_config_ignores_comments(temp_config_file):
    """Test that comments are ignored"""
    cm = ConfigManager(config_path=temp_config_file)

    # Comments should not be in config
    assert "# Test config file" not in cm.config
    assert "# Comment line" not in cm.config


def test_config_manager_load_config_ignores_empty_lines(temp_config_file):
    """Test that empty lines are ignored"""
    cm = ConfigManager(config_path=temp_config_file)

    # Should have exactly 4 keys
    assert len(cm.config) == 4


def test_config_manager_load_config_file_not_found():
    """Test loading config when file doesn't exist"""
    cm = ConfigManager(config_path="/nonexistent/.env")

    assert cm.config == {}


def test_config_manager_get_existing_key(temp_config_file):
    """Test getting existing configuration value"""
    cm = ConfigManager(config_path=temp_config_file)

    value = cm.get("KEY1")

    assert value == "value1"


def test_config_manager_get_nonexistent_key(temp_config_file):
    """Test getting non-existent key returns None"""
    cm = ConfigManager(config_path=temp_config_file)

    value = cm.get("NONEXISTENT")

    assert value is None


def test_config_manager_get_with_default(temp_config_file):
    """Test getting non-existent key with default value"""
    cm = ConfigManager(config_path=temp_config_file)

    value = cm.get("NONEXISTENT", "default_value")

    assert value == "default_value"


def test_config_manager_set(temp_config_file):
    """Test setting configuration value"""
    cm = ConfigManager(config_path=temp_config_file)

    cm.set("NEW_KEY", "new_value")

    assert cm.get("NEW_KEY") == "new_value"


def test_config_manager_set_overwrite(temp_config_file):
    """Test overwriting existing configuration value"""
    cm = ConfigManager(config_path=temp_config_file)

    original = cm.get("KEY1")
    cm.set("KEY1", "new_value")

    assert cm.get("KEY1") == "new_value"
    assert cm.get("KEY1") != original


def test_config_manager_get_all(temp_config_file):
    """Test getting all configuration"""
    cm = ConfigManager(config_path=temp_config_file)

    all_config = cm.get_all()

    assert isinstance(all_config, dict)
    assert "KEY1" in all_config
    assert "KEY2" in all_config
    assert len(all_config) == 4


def test_config_manager_get_all_returns_copy(temp_config_file):
    """Test that get_all returns a copy, not reference"""
    cm = ConfigManager(config_path=temp_config_file)

    all_config = cm.get_all()
    all_config["NEW_KEY"] = "new_value"

    # Original config should not be modified
    assert "NEW_KEY" not in cm.config
    assert cm.get("NEW_KEY") is None


def test_config_manager_reload_config(temp_config_file):
    """Test reloading configuration"""
    cm = ConfigManager(config_path=temp_config_file)

    # Get original value
    original_value = cm.get("KEY1")

    # Modify existing key in memory
    cm.set("KEY1", "modified_value")
    assert cm.get("KEY1") == "modified_value"

    # Reload from file
    result = cm.reload_config()

    assert result is True
    # KEY1 should be back to original value from file
    assert cm.get("KEY1") == original_value


def test_config_manager_reload_config_file_not_found():
    """Test reloading when file doesn't exist"""
    cm = ConfigManager(config_path="/nonexistent/.env")

    result = cm.reload_config()

    assert result is False


def test_config_manager_empty_file(empty_config_file):
    """Test loading empty config file"""
    cm = ConfigManager(config_path=empty_config_file)

    assert cm.config == {}


def test_config_manager_malformed_line():
    """Test handling malformed config lines"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("VALID_KEY=valid_value\n")
        f.write("INVALID_LINE_NO_EQUALS\n")
        f.write("ANOTHER_VALID=value\n")
        temp_path = f.name

    try:
        cm = ConfigManager(config_path=temp_path)

        # Valid keys should be loaded
        assert cm.get("VALID_KEY") == "valid_value"
        assert cm.get("ANOTHER_VALID") == "value"
        # Invalid line should be ignored
        assert "INVALID_LINE_NO_EQUALS" not in cm.config
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_config_manager_load_config_with_exception(monkeypatch):
    """Test load_config when an exception occurs"""
    cm = ConfigManager(config_path="test.env")

    # Mock open to raise an exception
    def mock_open(*args, **kwargs):
        raise PermissionError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    # Create a file so exists() returns True
    Path("test.env").touch()

    try:
        result = cm.load_config()
        assert result is False
    finally:
        Path("test.env").unlink(missing_ok=True)
