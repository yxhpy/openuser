"""
Tests for Agent API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from src.api.main import create_app
from src.core.agent_manager import Agent, AgentManager
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
def sample_agent():
    """Sample agent for testing."""
    return Agent(
        name="test-agent",
        system_prompt="You are a helpful assistant",
        capabilities=["chat", "code"]
    )


@pytest.fixture
def mock_agent_manager(sample_agent):
    """Create mock agent manager."""
    manager = Mock(spec=AgentManager)
    manager.list_agents = Mock(return_value=["test-agent"])
    manager.get_agent = Mock(return_value=sample_agent)
    manager.create_agent = Mock(return_value=sample_agent)
    manager.update_agent = Mock(return_value=sample_agent)
    manager.delete_agent = Mock(return_value=True)
    return manager


@pytest.fixture
def client(mock_user, mock_agent_manager):
    """Create test client with overridden dependencies."""
    app = create_app()

    def override_get_current_user():
        return mock_user

    def override_get_agent_manager():
        return mock_agent_manager

    from src.api import agents
    app.dependency_overrides[agents.get_current_user] = override_get_current_user
    app.dependency_overrides[agents.get_agent_manager] = override_get_agent_manager

    return TestClient(app)


def test_create_agent(client, auth_token, mock_agent_manager):
    """Test creating a new agent."""
    mock_agent_manager.get_agent.return_value = None

    response = client.post(
        "/api/v1/agents/create",
        json={
            "name": "test-agent",
            "system_prompt": "You are a helpful assistant",
            "capabilities": ["chat", "code"]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test-agent"
    assert data["system_prompt"] == "You are a helpful assistant"
    assert data["capabilities"] == ["chat", "code"]


def test_create_agent_already_exists(client, auth_token, mock_agent_manager, sample_agent):
    """Test creating an agent that already exists."""
    mock_agent_manager.get_agent.return_value = sample_agent

    response = client.post(
        "/api/v1/agents/create",
        json={
            "name": "test-agent",
            "system_prompt": "You are a helpful assistant",
            "capabilities": ["chat", "code"]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_agent_unauthorized():
    """Test creating an agent without authentication."""
    # Create a fresh app without dependency overrides
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/api/v1/agents/create",
        json={
            "name": "test-agent",
            "system_prompt": "You are a helpful assistant",
            "capabilities": ["chat", "code"]
        }
    )

    assert response.status_code == 401


def test_list_agents(client, auth_token):
    """Test listing all agents."""
    response = client.get(
        "/api/v1/agents/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["agents"]) == 1
    assert data["agents"][0]["name"] == "test-agent"


def test_list_agents_empty(client, auth_token, mock_agent_manager):
    """Test listing agents when none exist."""
    mock_agent_manager.list_agents.return_value = []

    response = client.get(
        "/api/v1/agents/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["agents"]) == 0


def test_get_agent(client, auth_token):
    """Test getting agent details."""
    response = client.get(
        "/api/v1/agents/test-agent",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-agent"
    assert data["system_prompt"] == "You are a helpful assistant"


def test_get_agent_not_found(client, auth_token, mock_agent_manager):
    """Test getting a non-existent agent."""
    mock_agent_manager.get_agent.return_value = None

    response = client.get(
        "/api/v1/agents/nonexistent",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


def test_update_agent(client, auth_token, mock_agent_manager):
    """Test updating an agent."""
    updated_agent = Agent(
        name="test-agent",
        system_prompt="Updated prompt",
        capabilities=["chat", "code", "search"]
    )
    mock_agent_manager.update_agent.return_value = updated_agent

    response = client.put(
        "/api/v1/agents/test-agent",
        json={
            "system_prompt": "Updated prompt",
            "capabilities": ["chat", "code", "search"]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["system_prompt"] == "Updated prompt"
    assert len(data["capabilities"]) == 3


def test_update_agent_not_found(client, auth_token, mock_agent_manager):
    """Test updating a non-existent agent."""
    mock_agent_manager.update_agent.return_value = None

    response = client.put(
        "/api/v1/agents/nonexistent",
        json={
            "system_prompt": "Updated prompt"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


def test_delete_agent(client, auth_token):
    """Test deleting an agent."""
    response = client.delete(
        "/api/v1/agents/test-agent",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 204


def test_delete_agent_not_found(client, auth_token, mock_agent_manager):
    """Test deleting a non-existent agent."""
    mock_agent_manager.delete_agent.return_value = False

    response = client.delete(
        "/api/v1/agents/nonexistent",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


def test_get_agent_manager_dependency():
    """Test get_agent_manager dependency."""
    from src.api.agents import get_agent_manager

    manager = get_agent_manager()
    assert isinstance(manager, AgentManager)


def test_create_agent_exception(client, auth_token, mock_agent_manager):
    """Test creating an agent with exception."""
    mock_agent_manager.get_agent.return_value = None
    mock_agent_manager.create_agent.side_effect = Exception("Test error")

    response = client.post(
        "/api/v1/agents/create",
        json={
            "name": "test-agent",
            "system_prompt": "You are a helpful assistant",
            "capabilities": ["chat", "code"]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 500
    assert "Failed to create agent" in response.json()["detail"]


def test_list_agents_exception(client, auth_token, mock_agent_manager):
    """Test listing agents with exception."""
    mock_agent_manager.list_agents.side_effect = Exception("Test error")

    response = client.get(
        "/api/v1/agents/list",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 500
    assert "Failed to list agents" in response.json()["detail"]


def test_update_agent_exception(client, auth_token, mock_agent_manager):
    """Test updating an agent with exception."""
    mock_agent_manager.update_agent.side_effect = Exception("Test error")

    response = client.put(
        "/api/v1/agents/test-agent",
        json={
            "system_prompt": "Updated prompt"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 500
    assert "Failed to update agent" in response.json()["detail"]
