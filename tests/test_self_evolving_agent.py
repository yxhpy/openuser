"""
Tests for self-evolving agent system.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.core.self_evolving_agent import (
    AgentContext,
    PluginCreator,
    SelfEvolvingAgent,
)
from src.core.plugin_manager import PluginManager


class TestAgentContext:
    """Tests for AgentContext class."""

    def test_init(self):
        """Test context initialization."""
        context = AgentContext(max_history=50)
        assert context.max_history == 50
        assert len(context.interactions) == 0
        assert len(context.learned_patterns) == 0
        assert len(context.environment) == 0

    def test_add_interaction(self):
        """Test adding interaction."""
        context = AgentContext()
        context.add_interaction("Hello", "Hi there", {"test": True})

        assert len(context.interactions) == 1
        interaction = context.interactions[0]
        assert interaction["user_input"] == "Hello"
        assert interaction["agent_response"] == "Hi there"
        assert interaction["metadata"]["test"] is True
        assert "timestamp" in interaction

    def test_add_interaction_max_history(self):
        """Test interaction history limit."""
        context = AgentContext(max_history=3)

        for i in range(5):
            context.add_interaction(f"Input {i}", f"Response {i}")

        assert len(context.interactions) == 3
        # Should keep the last 3 interactions
        assert context.interactions[0]["user_input"] == "Input 2"
        assert context.interactions[-1]["user_input"] == "Input 4"

    def test_get_recent_interactions(self):
        """Test getting recent interactions."""
        context = AgentContext()

        for i in range(10):
            context.add_interaction(f"Input {i}", f"Response {i}")

        recent = context.get_recent_interactions(3)
        assert len(recent) == 3
        assert recent[0]["user_input"] == "Input 7"
        assert recent[-1]["user_input"] == "Input 9"

    def test_learn_pattern(self):
        """Test learning a pattern."""
        context = AgentContext()
        context.learn_pattern("test_pattern", {"key": "value"})

        assert "test_pattern" in context.learned_patterns
        pattern = context.learned_patterns["test_pattern"]
        assert pattern["data"] == {"key": "value"}
        assert pattern["usage_count"] == 0
        assert "learned_at" in pattern

    def test_get_pattern(self):
        """Test retrieving a pattern."""
        context = AgentContext()
        context.learn_pattern("test_pattern", {"key": "value"})

        # First retrieval
        data = context.get_pattern("test_pattern")
        assert data == {"key": "value"}
        assert context.learned_patterns["test_pattern"]["usage_count"] == 1

        # Second retrieval
        data = context.get_pattern("test_pattern")
        assert context.learned_patterns["test_pattern"]["usage_count"] == 2

    def test_get_pattern_not_found(self):
        """Test retrieving non-existent pattern."""
        context = AgentContext()
        data = context.get_pattern("nonexistent")
        assert data is None

    def test_update_environment(self):
        """Test updating environment parameter."""
        context = AgentContext()
        context.update_environment("key1", "value1")
        context.update_environment("key2", 42)

        assert context.environment["key1"] == "value1"
        assert context.environment["key2"] == 42

    def test_get_environment(self):
        """Test getting environment parameter."""
        context = AgentContext()
        context.update_environment("key1", "value1")

        assert context.get_environment("key1") == "value1"
        assert context.get_environment("nonexistent") is None
        assert context.get_environment("nonexistent", "default") == "default"

    def test_to_dict(self):
        """Test converting context to dictionary."""
        context = AgentContext()
        context.add_interaction("Hello", "Hi")
        context.learn_pattern("pattern1", {"data": "test"})
        context.update_environment("env1", "value1")

        data = context.to_dict()
        assert "interactions" in data
        assert "learned_patterns" in data
        assert "environment" in data
        assert len(data["interactions"]) == 1
        assert "pattern1" in data["learned_patterns"]
        assert data["environment"]["env1"] == "value1"

    def test_from_dict(self):
        """Test loading context from dictionary."""
        context = AgentContext()
        data = {
            "interactions": [{"user_input": "test", "agent_response": "response"}],
            "learned_patterns": {"pattern1": {"data": "test"}},
            "environment": {"env1": "value1"},
        }

        context.from_dict(data)
        assert len(context.interactions) == 1
        assert "pattern1" in context.learned_patterns
        assert context.environment["env1"] == "value1"


class TestPluginCreator:
    """Tests for PluginCreator class."""

    def test_generate_plugin_template(self):
        """Test generating plugin template."""
        template = PluginCreator.generate_plugin_template(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            capabilities=["cap1", "cap2"],
        )

        assert "test_plugin" in template
        assert "1.0.0" in template
        assert "Test plugin" in template
        assert "cap1" in template
        assert "cap2" in template
        assert "class TestPluginPlugin" in template  # Fixed: capital P

    def test_create_plugin_success(self, tmp_path):
        """Test creating a plugin successfully."""
        plugin_code = 'print("test plugin")'
        success, message = PluginCreator.create_plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test",
            plugin_code=plugin_code,
            output_dir=str(tmp_path),
        )

        assert success is True
        assert "created successfully" in message
        plugin_file = tmp_path / "test_plugin.py"
        assert plugin_file.exists()
        assert plugin_file.read_text() == plugin_code

    def test_create_plugin_already_exists(self, tmp_path):
        """Test creating a plugin that already exists."""
        plugin_file = tmp_path / "test_plugin.py"
        plugin_file.write_text("existing")

        success, message = PluginCreator.create_plugin(
            name="test_plugin",
            version="1.0.0",
            description="Test",
            plugin_code="new code",
            output_dir=str(tmp_path),
        )

        assert success is False
        assert "already exists" in message


class TestSelfEvolvingAgent:
    """Tests for SelfEvolvingAgent class."""

    @pytest.fixture
    def mock_plugin_manager(self):
        """Create mock plugin manager."""
        return Mock(spec=PluginManager)

    @pytest.fixture
    def agent(self, mock_plugin_manager, tmp_path):
        """Create test agent."""
        context_file = str(tmp_path / "test_context.json")
        return SelfEvolvingAgent(
            name="test_agent",
            system_prompt="Test prompt",
            capabilities=["test_cap"],
            plugin_manager=mock_plugin_manager,
            context_file=context_file,
        )

    def test_init(self, agent):
        """Test agent initialization."""
        assert agent.name == "test_agent"
        assert agent.system_prompt == "Test prompt"
        assert "test_cap" in agent.capabilities
        assert agent.context is not None
        assert agent.plugin_manager is not None
        assert agent.plugin_creator is not None

    def test_self_update_prompt(self, agent):
        """Test self-updating prompt."""
        result = agent.self_update_prompt("New prompt", "Testing update")

        assert result["status"] == "success"
        assert agent.system_prompt == "New prompt"
        assert "update_record" in result
        assert result["update_record"]["reason"] == "Testing update"

    def test_auto_install_plugin_success(self, agent):
        """Test auto-installing plugin successfully."""
        mock_plugin = Mock()
        mock_plugin.capabilities = ["new_cap1", "new_cap2"]
        agent.plugin_manager.get_plugin.return_value = None
        agent.plugin_manager.load_plugin.return_value = mock_plugin

        result = agent.auto_install_plugin("test_plugin", "Need this plugin")

        assert result["status"] == "success"
        assert "new_cap1" in agent.capabilities
        assert "new_cap2" in agent.capabilities
        agent.plugin_manager.load_plugin.assert_called_once_with("test_plugin")

    def test_auto_install_plugin_already_installed(self, agent):
        """Test auto-installing already installed plugin."""
        agent.plugin_manager.get_plugin.return_value = Mock()

        result = agent.auto_install_plugin("test_plugin", "Need this plugin")

        assert result["status"] == "already_installed"
        agent.plugin_manager.load_plugin.assert_not_called()

    def test_auto_install_plugin_error(self, agent):
        """Test auto-installing plugin with error."""
        agent.plugin_manager.get_plugin.return_value = None
        agent.plugin_manager.load_plugin.side_effect = Exception("Load failed")

        result = agent.auto_install_plugin("test_plugin", "Need this plugin")

        assert result["status"] == "error"
        assert "Load failed" in result["message"]

    def test_create_custom_plugin_with_template(self, agent, tmp_path):
        """Test creating custom plugin with template."""
        agent.plugin_creator.create_plugin = Mock(return_value=(True, "Success"))

        result = agent.create_custom_plugin(
            name="custom_plugin",
            version="1.0.0",
            description="Custom plugin",
            capabilities=["cap1"],
        )

        assert result["status"] == "success"
        agent.plugin_creator.create_plugin.assert_called_once()

    def test_create_custom_plugin_with_custom_code(self, agent):
        """Test creating custom plugin with custom code."""
        agent.plugin_creator.create_plugin = Mock(return_value=(True, "Success"))

        result = agent.create_custom_plugin(
            name="custom_plugin",
            version="1.0.0",
            description="Custom plugin",
            capabilities=["cap1"],
            custom_code="print('custom')",
        )

        assert result["status"] == "success"
        # Check that create_plugin was called with custom code
        call_args = agent.plugin_creator.create_plugin.call_args
        assert call_args[0][3] == "print('custom')"  # plugin_code is 4th positional arg

    def test_create_custom_plugin_error(self, agent):
        """Test creating custom plugin with error."""
        agent.plugin_creator.create_plugin = Mock(return_value=(False, "Error occurred"))

        result = agent.create_custom_plugin(
            name="custom_plugin",
            version="1.0.0",
            description="Custom plugin",
            capabilities=["cap1"],
        )

        assert result["status"] == "error"
        assert "Error occurred" in result["message"]

    def test_adjust_environment(self, agent):
        """Test adjusting environment parameter."""
        result = agent.adjust_environment("param1", "value1", "Testing adjustment")

        assert result["status"] == "success"
        assert agent.context.get_environment("param1") == "value1"
        assert result["adjustment_record"]["reason"] == "Testing adjustment"

    @pytest.mark.asyncio
    async def test_process_standard(self, agent):
        """Test standard processing."""
        input_data = {"input": "Hello agent"}

        result = await agent.process(input_data)

        assert result["status"] == "success"
        assert len(agent.context.interactions) == 1

    @pytest.mark.asyncio
    async def test_process_with_error(self, agent):
        """Test processing with error."""
        agent._make_decision = Mock(side_effect=Exception("Decision failed"))

        input_data = {"input": "Test input"}
        result = await agent.process(input_data)

        assert result["status"] == "error"
        assert "Decision failed" in result["message"]

    def test_make_decision_install_plugin(self, agent):
        """Test decision making for plugin installation."""
        decision = agent._make_decision("I need to install plugin X", [])

        assert decision["action"] == "install_plugin"
        assert "plugin installation" in decision["reasoning"].lower()

    def test_make_decision_self_update(self, agent):
        """Test decision making for self-update."""
        decision = agent._make_decision("Please update prompt to be more helpful", [])

        assert decision["action"] == "self_update"
        assert "behavior update" in decision["reasoning"].lower()

    def test_make_decision_create_plugin(self, agent):
        """Test decision making for plugin creation."""
        decision = agent._make_decision("Create a new plugin for me", [])

        assert decision["action"] == "create_plugin"
        assert "plugin creation" in decision["reasoning"].lower()

    def test_make_decision_standard(self, agent):
        """Test standard decision making."""
        decision = agent._make_decision("Just a normal question", [])

        assert decision["action"] == "process"

    def test_analyze_interaction_patterns(self, agent):
        """Test analyzing interaction patterns."""
        interactions = [
            {"user_input": "testing something important"},
            {"user_input": "another testing question"},
            {"user_input": "testing again"},
        ]

        patterns = agent._analyze_interaction_patterns(interactions)

        assert "frequent_topics" in patterns
        assert "testing" in patterns["frequent_topics"]

    @pytest.mark.asyncio
    async def test_execute_decision_install_plugin(self, agent):
        """Test executing install plugin decision."""
        agent.plugin_manager.get_plugin.return_value = None
        mock_plugin = Mock()
        mock_plugin.capabilities = ["cap1"]
        agent.plugin_manager.load_plugin.return_value = mock_plugin

        decision = {"action": "install_plugin", "reasoning": "Test"}
        input_data = {"plugin_name": "test_plugin"}

        result = await agent._execute_decision(decision, input_data)

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_execute_decision_self_update(self, agent):
        """Test executing self-update decision."""
        decision = {"action": "self_update", "reasoning": "Test"}
        input_data = {"new_prompt": "Updated prompt"}

        result = await agent._execute_decision(decision, input_data)

        assert result["status"] == "success"
        assert agent.system_prompt == "Updated prompt"

    @pytest.mark.asyncio
    async def test_execute_decision_create_plugin(self, agent):
        """Test executing create plugin decision."""
        agent.plugin_creator.create_plugin = Mock(return_value=(True, "Success"))

        decision = {"action": "create_plugin", "reasoning": "Test"}
        input_data = {
            "name": "new_plugin",
            "version": "1.0.0",
            "description": "Test",
            "capabilities": ["cap1"],
        }

        result = await agent._execute_decision(decision, input_data)

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_handle_error(self, agent):
        """Test error handling."""
        error = Exception("Test error")
        input_data = {"input": "test"}

        result = await agent._handle_error(error, input_data)

        assert result["status"] == "error"
        assert "Test error" in result["message"]
        assert "recovery" in result
        assert len(agent.error_history) > 0

    def test_record_error(self, agent):
        """Test recording error."""
        agent._record_error("test_error", "Error message", {"context": "test"})

        assert len(agent.error_history) == 1
        error = agent.error_history[0]
        assert error["type"] == "test_error"
        assert error["message"] == "Error message"
        assert error["context"]["context"] == "test"

    def test_record_error_max_history(self, agent):
        """Test error history limit."""
        for i in range(150):
            agent._record_error(f"error_{i}", f"Message {i}", {})

        assert len(agent.error_history) == 100

    def test_attempt_recovery_new_error(self, agent):
        """Test recovery attempt for new error."""
        error = Exception("New error")
        result = agent._attempt_recovery(error, {})

        assert result["status"] == "new_error"

    def test_attempt_recovery_known_error(self, agent):
        """Test recovery attempt for known error."""
        error = Exception("Known error")
        agent._record_error("test", "Known error", {})
        agent._record_error("test", "Known error", {})

        result = agent._attempt_recovery(error, {})

        assert result["status"] == "known_error"
        assert result["occurrences"] == 2

    def test_save_and_load_context(self, agent, tmp_path):
        """Test saving and loading context."""
        # Add some data
        agent.context.add_interaction("Hello", "Hi")
        agent.context.learn_pattern("pattern1", {"data": "test"})
        agent._record_error("test_error", "Error", {})

        # Save context
        agent._save_context()

        # Create new agent and load context
        new_agent = SelfEvolvingAgent(
            name="test_agent",
            system_prompt="Test",
            context_file=agent.context_file,
        )

        assert len(new_agent.context.interactions) == 1
        assert "pattern1" in new_agent.context.learned_patterns
        assert len(new_agent.error_history) == 1

    def test_get_learning_stats(self, agent):
        """Test getting learning statistics."""
        agent.context.add_interaction("Hello", "Hi")
        agent.context.learn_pattern("pattern1", {"data": "test"})
        agent.context.update_environment("env1", "value1")
        agent._record_error("error1", "Error", {})
        agent.decision_history.append({"decision": "test"})

        stats = agent.get_learning_stats()

        assert stats["total_interactions"] == 1
        assert stats["learned_patterns"] == 1
        assert stats["environment_params"] == 1
        assert stats["total_errors"] == 1
        assert stats["total_decisions"] == 1
        assert "test_cap" in stats["capabilities"]
