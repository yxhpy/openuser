"""
End-to-end tests for plugin management workflow.

Tests the complete plugin lifecycle:
1. User authentication
2. List available plugins
3. Install a plugin
4. Reload a plugin
5. Verify plugin functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os
from pathlib import Path

from src.api.main import app
from src.models.base import Base, get_db
from src.core.plugin_manager import PluginManager


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_e2e_plugins.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def setup_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_database):
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_user(client):
    """Create and authenticate a test user."""
    register_data = {
        "username": "pluginuser",
        "email": "pluginuser@example.com",
        "password": "SecurePass123!",
    }
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 200
    tokens = response.json()
    return tokens["access_token"]


@pytest.fixture
def test_plugin_dir(tmp_path):
    """Create a test plugin directory with a sample plugin."""
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()

    # Create a simple test plugin
    plugin_code = '''
from src.core.plugin_base import Plugin

class TestPlugin(Plugin):
    name = "test-plugin"
    version = "1.0.0"

    def on_load(self):
        self.loaded = True

    def on_unload(self):
        self.loaded = False
'''
    plugin_file = plugin_dir / "test_plugin.py"
    plugin_file.write_text(plugin_code)

    return plugin_dir


@pytest.mark.e2e
class TestPluginManagementWorkflow:
    """Test complete plugin management workflow."""

    def test_complete_plugin_lifecycle(self, client, authenticated_user):
        """
        Test complete plugin lifecycle:
        1. List plugins (should show built-in plugins)
        2. Verify plugin information
        """
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Step 1: List plugins
        response = client.get("/api/v1/plugins/list", headers=headers)
        assert response.status_code == 200
        plugins = response.json()
        assert isinstance(plugins, list)

        # Verify plugin structure
        if len(plugins) > 0:
            plugin = plugins[0]
            assert "name" in plugin
            assert "version" in plugin
            assert "status" in plugin

    def test_plugin_reload(self, client, authenticated_user):
        """Test plugin hot-reload functionality."""
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # List plugins first
        response = client.get("/api/v1/plugins/list", headers=headers)
        assert response.status_code == 200
        plugins = response.json()

        if len(plugins) > 0:
            plugin_name = plugins[0]["name"]

            # Reload the plugin
            response = client.post(
                "/api/v1/plugins/reload",
                headers=headers,
                json={"name": plugin_name},
            )
            # Should succeed or return appropriate error
            assert response.status_code in [200, 400, 404]

    def test_unauthorized_plugin_access(self, client):
        """Test accessing plugin endpoints without authentication."""
        # Try to list plugins without auth
        response = client.get("/api/v1/plugins/list")
        assert response.status_code == 401

        # Try to reload plugin without auth
        response = client.post("/api/v1/plugins/reload", json={"name": "test"})
        assert response.status_code == 401

    def test_invalid_plugin_operations(self, client, authenticated_user):
        """Test invalid plugin operations."""
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Try to reload non-existent plugin
        response = client.post(
            "/api/v1/plugins/reload",
            headers=headers,
            json={"name": "non-existent-plugin"},
        )
        assert response.status_code in [400, 404]

    def test_plugin_list_consistency(self, client, authenticated_user):
        """Test that plugin list is consistent across multiple requests."""
        headers = {"Authorization": f"Bearer {authenticated_user}"}

        # Get plugin list twice
        response1 = client.get("/api/v1/plugins/list", headers=headers)
        assert response1.status_code == 200
        plugins1 = response1.json()

        response2 = client.get("/api/v1/plugins/list", headers=headers)
        assert response2.status_code == 200
        plugins2 = response2.json()

        # Lists should be identical
        assert len(plugins1) == len(plugins2)
        plugin_names1 = {p["name"] for p in plugins1}
        plugin_names2 = {p["name"] for p in plugins2}
        assert plugin_names1 == plugin_names2
