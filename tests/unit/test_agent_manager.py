"""Tests for Agent Manager"""

import pytest
from src.core.agent_manager import AgentManager, Agent


class TestAgent(Agent):
    """Test agent implementation"""

    async def process(self, input_data: dict) -> dict:
        """Process input data"""
        return {"status": "processed", "input": input_data}


def test_agent_init() -> None:
    """Test Agent initialization"""
    agent = Agent(
        name="test-agent",
        system_prompt="You are a test agent",
        capabilities=["test", "demo"]
    )

    assert agent.name == "test-agent"
    assert agent.system_prompt == "You are a test agent"
    assert agent.capabilities == ["test", "demo"]
    assert agent._memory == []


def test_agent_init_without_capabilities() -> None:
    """Test Agent initialization without capabilities"""
    agent = Agent(
        name="test-agent",
        system_prompt="You are a test agent"
    )

    assert agent.capabilities == []


@pytest.mark.asyncio
async def test_agent_process_not_implemented() -> None:
    """Test that base Agent.process raises NotImplementedError"""
    agent = Agent(
        name="test-agent",
        system_prompt="You are a test agent"
    )

    with pytest.raises(NotImplementedError):
        await agent.process({"test": "data"})


@pytest.mark.asyncio
async def test_agent_process_implemented() -> None:
    """Test agent process when implemented"""
    agent = TestAgent(
        name="test-agent",
        system_prompt="You are a test agent"
    )

    result = await agent.process({"test": "data"})

    assert result["status"] == "processed"
    assert result["input"] == {"test": "data"}


def test_agent_update_prompt() -> None:
    """Test updating agent prompt"""
    agent = Agent(
        name="test-agent",
        system_prompt="Original prompt"
    )

    agent.update_prompt("New prompt")

    assert agent.system_prompt == "New prompt"


def test_agent_add_capability() -> None:
    """Test adding capability to agent"""
    agent = Agent(
        name="test-agent",
        system_prompt="Test prompt",
        capabilities=["existing"]
    )

    agent.add_capability("new-capability")

    assert "new-capability" in agent.capabilities
    assert "existing" in agent.capabilities


def test_agent_add_duplicate_capability() -> None:
    """Test adding duplicate capability (should not add)"""
    agent = Agent(
        name="test-agent",
        system_prompt="Test prompt",
        capabilities=["existing"]
    )

    agent.add_capability("existing")

    # Should still have only one "existing"
    assert agent.capabilities.count("existing") == 1


def test_agent_remove_capability() -> None:
    """Test removing capability from agent"""
    agent = Agent(
        name="test-agent",
        system_prompt="Test prompt",
        capabilities=["cap1", "cap2", "cap3"]
    )

    agent.remove_capability("cap2")

    assert "cap2" not in agent.capabilities
    assert "cap1" in agent.capabilities
    assert "cap3" in agent.capabilities


def test_agent_remove_nonexistent_capability() -> None:
    """Test removing non-existent capability (should do nothing)"""
    agent = Agent(
        name="test-agent",
        system_prompt="Test prompt",
        capabilities=["cap1"]
    )

    agent.remove_capability("nonexistent")

    # Should still have cap1
    assert agent.capabilities == ["cap1"]


def test_agent_manager_init() -> None:
    """Test AgentManager initialization"""
    am = AgentManager()

    assert am is not None
    assert am.agents == {}


def test_agent_manager_create_agent() -> None:
    """Test creating an agent"""
    am = AgentManager()

    agent = am.create_agent(
        name="test-agent",
        system_prompt="Test prompt",
        capabilities=["test"]
    )

    assert agent is not None
    assert agent.name == "test-agent"
    assert agent.system_prompt == "Test prompt"
    assert agent.capabilities == ["test"]
    assert "test-agent" in am.agents


def test_agent_manager_create_agent_without_capabilities() -> None:
    """Test creating an agent without capabilities"""
    am = AgentManager()

    agent = am.create_agent(
        name="test-agent",
        system_prompt="Test prompt"
    )

    assert agent.capabilities == []


def test_agent_manager_get_agent() -> None:
    """Test getting an agent"""
    am = AgentManager()

    # Create agent
    created = am.create_agent(
        name="test-agent",
        system_prompt="Test prompt"
    )

    # Get agent
    retrieved = am.get_agent("test-agent")

    assert retrieved is created
    assert retrieved.name == "test-agent"


def test_agent_manager_get_nonexistent_agent() -> None:
    """Test getting non-existent agent"""
    am = AgentManager()

    agent = am.get_agent("nonexistent")

    assert agent is None


def test_agent_manager_update_agent_prompt() -> None:
    """Test updating agent prompt"""
    am = AgentManager()

    # Create agent
    am.create_agent(
        name="test-agent",
        system_prompt="Original prompt"
    )

    # Update prompt
    updated = am.update_agent(
        name="test-agent",
        system_prompt="New prompt"
    )

    assert updated is not None
    assert updated.system_prompt == "New prompt"


def test_agent_manager_update_agent_capabilities() -> None:
    """Test updating agent capabilities"""
    am = AgentManager()

    # Create agent
    am.create_agent(
        name="test-agent",
        system_prompt="Test prompt",
        capabilities=["old"]
    )

    # Update capabilities
    updated = am.update_agent(
        name="test-agent",
        capabilities=["new1", "new2"]
    )

    assert updated is not None
    assert updated.capabilities == ["new1", "new2"]


def test_agent_manager_update_agent_both() -> None:
    """Test updating both prompt and capabilities"""
    am = AgentManager()

    # Create agent
    am.create_agent(
        name="test-agent",
        system_prompt="Original prompt",
        capabilities=["old"]
    )

    # Update both
    updated = am.update_agent(
        name="test-agent",
        system_prompt="New prompt",
        capabilities=["new"]
    )

    assert updated is not None
    assert updated.system_prompt == "New prompt"
    assert updated.capabilities == ["new"]


def test_agent_manager_update_nonexistent_agent() -> None:
    """Test updating non-existent agent"""
    am = AgentManager()

    updated = am.update_agent(
        name="nonexistent",
        system_prompt="New prompt"
    )

    assert updated is None


def test_agent_manager_delete_agent() -> None:
    """Test deleting an agent"""
    am = AgentManager()

    # Create agent
    am.create_agent(
        name="test-agent",
        system_prompt="Test prompt"
    )

    # Delete agent
    result = am.delete_agent("test-agent")

    assert result is True
    assert "test-agent" not in am.agents


def test_agent_manager_delete_nonexistent_agent() -> None:
    """Test deleting non-existent agent"""
    am = AgentManager()

    result = am.delete_agent("nonexistent")

    assert result is False


def test_agent_manager_list_agents() -> None:
    """Test listing agents"""
    am = AgentManager()

    # Initially empty
    assert am.list_agents() == []

    # Create agents
    am.create_agent("agent1", "Prompt 1")
    am.create_agent("agent2", "Prompt 2")
    am.create_agent("agent3", "Prompt 3")

    # List agents
    agents = am.list_agents()

    assert len(agents) == 3
    assert "agent1" in agents
    assert "agent2" in agents
    assert "agent3" in agents

