"""
Tests for Plugin API endpoints.
"""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.api.plugins import get_plugin_manager
from src.api.auth import get_current_user
from src.core.plugin_manager import Plugin, PluginManager
from src.api.auth_utils import create_access_token


@pytest.fixture
def mock_user():
    """Create mock user."""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    user.is_active = True
    return user


@pytest.fixture
def auth_token(mock_user):
    """Create authentication token."""
    return create_access_token({"sub": mock_user.username, "user_id": mock_user.id})


@pytest.fixture
def mock_plugin():
    """Create mock plugin."""
    plugin = Mock(spec=Plugin)
    plugin.name = "test_plugin"
    plugin.version = "1.0.0"
    plugin.dependencies = []
    return plugin


@pytest.fixture
def mock_plugin_manager(mock_plugin):
    """Create mock plugin manager."""
    manager = Mock(spec=PluginManager)
    manager.list_plugins = Mock(return_value=["test_plugin"])
    manager.get_plugin = Mock(return_value=mock_plugin)
    manager.load_plugin = Mock(return_value=mock_plugin)
    manager.reload_plugin = Mock(return_value=True)
    return manager


@pytest.fixture
def client(mock_user, mock_plugin_manager):
    """Create test client with overridden dependencies."""
    app = create_app()

    def override_get_current_user():
        return mock_user

    def override_get_plugin_manager():
        return mock_plugin_manager

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_plugin_manager] = override_get_plugin_manager

    return TestClient(app)


def test_list_plugins(client, auth_token):
    """Test listing plugins."""
    response = client.get(
        "/api/v1/plugins/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "plugins" in data
    assert "total" in data
    assert data["total"] == 1
    assert len(data["plugins"]) == 1
    assert data["plugins"][0]["name"] == "test_plugin"
    assert data["plugins"][0]["version"] == "1.0.0"


def test_list_plugins_empty(client, auth_token, mock_plugin_manager):
    """Test listing plugins when none are loaded."""
    mock_plugin_manager.list_plugins.return_value = []

    response = client.get(
        "/api/v1/plugins/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["plugins"]) == 0


def test_list_plugins_unauthorized():
    """Test listing plugins without authentication."""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/plugins/list")

    assert response.status_code == 401


def test_install_plugin(client, auth_token, mock_plugin_manager):
    """Test installing a plugin."""
    mock_plugin_manager.list_plugins.return_value = []

    response = client.post(
        "/api/v1/plugins/install",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "new_plugin"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_plugin"
    assert data["version"] == "1.0.0"
    assert "installed successfully" in data["message"]
    mock_plugin_manager.load_plugin.assert_called_once_with("new_plugin")


def test_install_plugin_already_installed(client, auth_token, mock_plugin_manager):
    """Test installing a plugin that's already installed."""
    response = client.post(
        "/api/v1/plugins/install",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "test_plugin"}
    )

    assert response.status_code == 400
    assert "already installed" in response.json()["detail"]


def test_install_plugin_failed(client, auth_token, mock_plugin_manager):
    """Test installing a plugin that fails to load."""
    mock_plugin_manager.list_plugins.return_value = []
    mock_plugin_manager.load_plugin.return_value = None

    response = client.post(
        "/api/v1/plugins/install",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "invalid_plugin"}
    )

    assert response.status_code == 400
    assert "Failed to install" in response.json()["detail"]


def test_reload_plugin(client, auth_token, mock_plugin_manager):
    """Test reloading a plugin."""
    response = client.post(
        "/api/v1/plugins/reload",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "test_plugin"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_plugin"
    assert data["version"] == "1.0.0"
    assert "reloaded successfully" in data["message"]
    mock_plugin_manager.reload_plugin.assert_called_once_with("test_plugin")


def test_reload_plugin_not_found(client, auth_token, mock_plugin_manager):
    """Test reloading a plugin that doesn't exist."""
    mock_plugin_manager.list_plugins.return_value = []

    response = client.post(
        "/api/v1/plugins/reload",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "nonexistent_plugin"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_reload_plugin_failed(client, auth_token, mock_plugin_manager):
    """Test reloading a plugin that fails."""
    mock_plugin_manager.reload_plugin.return_value = False

    response = client.post(
        "/api/v1/plugins/reload",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "test_plugin"}
    )

    assert response.status_code == 400
    assert "Failed to reload" in response.json()["detail"]


def test_get_plugin_manager_dependency():
    """Test get_plugin_manager dependency function."""
    from src.api.plugins import get_plugin_manager

    manager = get_plugin_manager()
    assert manager is not None
    assert isinstance(manager, PluginManager)
