"""
Self-Evolving Agent System

This module provides advanced agent capabilities including:
- Prompt-based self-update
- Auto-install plugins via prompts
- Create custom plugins programmatically
- Environment parameter adjustment
- Context awareness and learning
- Decision making and error recovery
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.agent_manager import Agent
from src.core.plugin_manager import PluginManager


class AgentContext:
    """Context manager for agent interactions and learning."""

    def __init__(self, max_history: int = 100):
        """
        Initialize agent context.

        Args:
            max_history: Maximum number of interactions to keep in history
        """
        self.interactions: List[Dict[str, Any]] = []
        self.max_history = max_history
        self.learned_patterns: Dict[str, Any] = {}
        self.environment: Dict[str, Any] = {}

    def add_interaction(
        self, user_input: str, agent_response: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an interaction to the context history.

        Args:
            user_input: User's input
            agent_response: Agent's response
            metadata: Additional metadata about the interaction
        """
        interaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_input": user_input,
            "agent_response": agent_response,
            "metadata": metadata or {},
        }
        self.interactions.append(interaction)

        # Keep only the most recent interactions
        if len(self.interactions) > self.max_history:
            self.interactions = self.interactions[-self.max_history :]

    def get_recent_interactions(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent interactions.

        Args:
            count: Number of recent interactions to retrieve

        Returns:
            List of recent interactions
        """
        return self.interactions[-count:]

    def learn_pattern(self, pattern_name: str, pattern_data: Any) -> None:
        """
        Learn a new pattern from interactions.

        Args:
            pattern_name: Name of the pattern
            pattern_data: Pattern data to store
        """
        self.learned_patterns[pattern_name] = {
            "data": pattern_data,
            "learned_at": datetime.utcnow().isoformat(),
            "usage_count": 0,
        }

    def get_pattern(self, pattern_name: str) -> Optional[Any]:
        """
        Retrieve a learned pattern.

        Args:
            pattern_name: Name of the pattern

        Returns:
            Pattern data if found, None otherwise
        """
        pattern = self.learned_patterns.get(pattern_name)
        if pattern:
            pattern["usage_count"] += 1
            return pattern["data"]
        return None

    def update_environment(self, key: str, value: Any) -> None:
        """
        Update environment parameter.

        Args:
            key: Environment parameter key
            value: Environment parameter value
        """
        self.environment[key] = value

    def get_environment(self, key: str, default: Any = None) -> Any:
        """
        Get environment parameter.

        Args:
            key: Environment parameter key
            default: Default value if key not found

        Returns:
            Environment parameter value
        """
        return self.environment.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary.

        Returns:
            Dictionary representation of context
        """
        return {
            "interactions": self.interactions,
            "learned_patterns": self.learned_patterns,
            "environment": self.environment,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load context from dictionary.

        Args:
            data: Dictionary containing context data
        """
        self.interactions = data.get("interactions", [])
        self.learned_patterns = data.get("learned_patterns", {})
        self.environment = data.get("environment", {})


class PluginCreator:
    """Helper class for creating custom plugins programmatically."""

    @staticmethod
    def create_plugin(
        name: str,
        version: str,
        description: str,
        plugin_code: str,
        output_dir: str = "src/plugins",
    ) -> Tuple[bool, str]:
        """
        Create a custom plugin programmatically.

        Args:
            name: Plugin name
            version: Plugin version
            description: Plugin description
            plugin_code: Python code for the plugin
            output_dir: Directory to save the plugin

        Returns:
            Tuple of (success, message/error)
        """
        try:
            # Create plugin directory if it doesn't exist
            plugin_dir = Path(output_dir)
            plugin_dir.mkdir(parents=True, exist_ok=True)

            # Generate plugin filename
            plugin_file = plugin_dir / f"{name}.py"

            # Check if plugin already exists
            if plugin_file.exists():
                return False, f"Plugin {name} already exists"

            # Write plugin code
            with open(plugin_file, "w") as f:
                f.write(plugin_code)

            return True, f"Plugin {name} created successfully at {plugin_file}"

        except Exception as e:
            return False, f"Failed to create plugin: {str(e)}"

    @staticmethod
    def generate_plugin_template(
        name: str, version: str, description: str, capabilities: List[str]
    ) -> str:
        """
        Generate a plugin template.

        Args:
            name: Plugin name
            version: Plugin version
            description: Plugin description
            capabilities: List of plugin capabilities

        Returns:
            Plugin code template
        """
        capabilities_str = "\n".join([f'        "{cap}",' for cap in capabilities])

        template = f'''"""
{description}
"""

from typing import Any, Dict
from src.core.plugin_manager import Plugin


class {name.title().replace("_", "")}Plugin(Plugin):
    """
    {description}
    """

    name = "{name}"
    version = "{version}"
    description = "{description}"
    capabilities = [
{capabilities_str}
    ]

    def on_load(self) -> None:
        """Called when plugin is loaded."""
        self.logger.info(f"{{self.name}} v{{self.version}} loaded")

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        self.logger.info(f"{{self.name}} unloaded")

    def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute plugin action.

        Args:
            action: Action to execute
            params: Action parameters

        Returns:
            Action result
        """
        if action == "example_action":
            return {{"status": "success", "message": "Example action executed"}}
        else:
            return {{"status": "error", "message": f"Unknown action: {{action}}"}}
'''
        return template


class SelfEvolvingAgent(Agent):
    """
    Self-evolving agent with advanced capabilities.

    Features:
    - Prompt-based self-update
    - Auto-install plugins
    - Create custom plugins programmatically
    - Environment parameter adjustment
    - Context awareness and learning
    - Decision making and error recovery
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        capabilities: Optional[List[str]] = None,
        plugin_manager: Optional[PluginManager] = None,
        context_file: Optional[str] = None,
    ):
        """
        Initialize self-evolving agent.

        Args:
            name: Agent name
            system_prompt: System prompt
            capabilities: Initial capabilities
            plugin_manager: Plugin manager instance
            context_file: Path to context persistence file
        """
        super().__init__(name, system_prompt, capabilities)
        self.context = AgentContext()
        self.plugin_manager = plugin_manager or PluginManager()
        self.plugin_creator = PluginCreator()
        self.context_file = context_file or f".agent_context_{name}.json"
        self.error_history: List[Dict[str, Any]] = []
        self.decision_history: List[Dict[str, Any]] = []

        # Load context if exists
        self._load_context()

    def self_update_prompt(self, new_prompt: str, reason: str) -> Dict[str, Any]:
        """
        Update agent's system prompt with reasoning.

        Args:
            new_prompt: New system prompt
            reason: Reason for the update

        Returns:
            Update result
        """
        old_prompt = self.system_prompt
        self.update_prompt(new_prompt)

        # Record the update
        update_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "old_prompt": old_prompt,
            "new_prompt": new_prompt,
            "reason": reason,
        }

        self.context.learn_pattern("prompt_updates", update_record)
        self._save_context()

        self.logger.info(f"Agent {self.name} self-updated prompt. Reason: {reason}")

        return {
            "status": "success",
            "message": "Prompt updated successfully",
            "update_record": update_record,
        }

    def auto_install_plugin(self, plugin_name: str, reason: str) -> Dict[str, Any]:
        """
        Automatically install a plugin when needed.

        Args:
            plugin_name: Name of the plugin to install
            reason: Reason for installing the plugin

        Returns:
            Installation result
        """
        try:
            # Check if plugin is already loaded
            if self.plugin_manager.get_plugin(plugin_name):
                return {
                    "status": "already_installed",
                    "message": f"Plugin {plugin_name} is already installed",
                }

            # Load the plugin
            plugin = self.plugin_manager.load_plugin(plugin_name)

            # Add plugin capabilities to agent
            if hasattr(plugin, "capabilities"):
                for capability in plugin.capabilities:
                    self.add_capability(capability)

            # Record the installation
            install_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "plugin_name": plugin_name,
                "reason": reason,
                "capabilities_added": getattr(plugin, "capabilities", []),
            }

            self.context.learn_pattern(f"plugin_install_{plugin_name}", install_record)
            self._save_context()

            self.logger.info(f"Agent {self.name} auto-installed plugin {plugin_name}. Reason: {reason}")

            return {
                "status": "success",
                "message": f"Plugin {plugin_name} installed successfully",
                "install_record": install_record,
            }

        except Exception as e:
            error_msg = f"Failed to install plugin {plugin_name}: {str(e)}"
            self.logger.error(error_msg)
            self._record_error("plugin_installation", error_msg, {"plugin_name": plugin_name})

            return {"status": "error", "message": error_msg}

    def create_custom_plugin(
        self, name: str, version: str, description: str, capabilities: List[str], custom_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a custom plugin programmatically.

        Args:
            name: Plugin name
            version: Plugin version
            description: Plugin description
            capabilities: Plugin capabilities
            custom_code: Custom plugin code (optional, uses template if not provided)

        Returns:
            Creation result
        """
        try:
            # Generate plugin code
            if custom_code:
                plugin_code = custom_code
            else:
                plugin_code = self.plugin_creator.generate_plugin_template(
                    name, version, description, capabilities
                )

            # Create the plugin file
            success, message = self.plugin_creator.create_plugin(name, version, description, plugin_code)

            if success:
                # Record the creation
                creation_record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "plugin_name": name,
                    "version": version,
                    "description": description,
                    "capabilities": capabilities,
                }

                self.context.learn_pattern(f"plugin_creation_{name}", creation_record)
                self._save_context()

                self.logger.info(f"Agent {self.name} created custom plugin {name}")

                return {
                    "status": "success",
                    "message": message,
                    "creation_record": creation_record,
                }
            else:
                return {"status": "error", "message": message}

        except Exception as e:
            error_msg = f"Failed to create plugin {name}: {str(e)}"
            self.logger.error(error_msg)
            self._record_error("plugin_creation", error_msg, {"plugin_name": name})

            return {"status": "error", "message": error_msg}

    def adjust_environment(self, key: str, value: Any, reason: str) -> Dict[str, Any]:
        """
        Adjust environment parameter.

        Args:
            key: Environment parameter key
            value: New value
            reason: Reason for the adjustment

        Returns:
            Adjustment result
        """
        old_value = self.context.get_environment(key)
        self.context.update_environment(key, value)

        # Record the adjustment
        adjustment_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "key": key,
            "old_value": old_value,
            "new_value": value,
            "reason": reason,
        }

        self.context.learn_pattern(f"env_adjustment_{key}", adjustment_record)
        self._save_context()

        self.logger.info(f"Agent {self.name} adjusted environment {key}={value}. Reason: {reason}")

        return {
            "status": "success",
            "message": f"Environment parameter {key} updated",
            "adjustment_record": adjustment_record,
        }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input with context awareness.

        Args:
            input_data: Input data from user

        Returns:
            Response data
        """
        try:
            user_input = input_data.get("input", "")

            # Get recent context
            recent_interactions = self.context.get_recent_interactions(5)

            # Make decision based on input and context
            decision = self._make_decision(user_input, recent_interactions)

            # Process based on decision
            response = await self._execute_decision(decision, input_data)

            # Record interaction
            self.context.add_interaction(
                user_input=user_input,
                agent_response=str(response),
                metadata={"decision": decision},
            )

            self._save_context()

            return response

        except Exception as e:
            return await self._handle_error(e, input_data)

    def _make_decision(self, user_input: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Make decision based on input and context.

        Args:
            user_input: User's input
            context: Recent interaction context

        Returns:
            Decision data
        """
        decision = {
            "timestamp": datetime.utcnow().isoformat(),
            "input": user_input,
            "action": "process",  # Default action
            "confidence": 1.0,
            "reasoning": "Standard processing",
        }

        # Check for plugin installation requests
        if "install plugin" in user_input.lower() or "need plugin" in user_input.lower():
            decision["action"] = "install_plugin"
            decision["reasoning"] = "User requested plugin installation"

        # Check for self-update requests
        elif "update prompt" in user_input.lower() or "change behavior" in user_input.lower():
            decision["action"] = "self_update"
            decision["reasoning"] = "User requested behavior update"

        # Check for plugin creation requests
        elif "create plugin" in user_input.lower() or "new plugin" in user_input.lower():
            decision["action"] = "create_plugin"
            decision["reasoning"] = "User requested plugin creation"

        # Learn from patterns
        if len(context) > 0:
            # Analyze patterns in recent interactions
            common_themes = self._analyze_interaction_patterns(context)
            if common_themes:
                decision["context_insights"] = common_themes

        self.decision_history.append(decision)
        return decision

    def _analyze_interaction_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in interactions.

        Args:
            interactions: List of interactions

        Returns:
            Pattern analysis
        """
        # Simple pattern analysis
        patterns = {"frequent_topics": [], "user_preferences": {}}

        # Count topic frequencies
        topics = {}
        for interaction in interactions:
            user_input = interaction.get("user_input", "").lower()
            # Simple keyword extraction
            for word in user_input.split():
                if len(word) > 4:  # Only consider words longer than 4 characters
                    topics[word] = topics.get(word, 0) + 1

        # Get top topics
        if topics:
            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            patterns["frequent_topics"] = [topic for topic, _ in sorted_topics[:3]]

        return patterns

    async def _execute_decision(self, decision: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute decision.

        Args:
            decision: Decision data
            input_data: Input data

        Returns:
            Execution result
        """
        action = decision.get("action", "process")

        if action == "install_plugin":
            plugin_name = input_data.get("plugin_name", "")
            return self.auto_install_plugin(plugin_name, decision.get("reasoning", ""))

        elif action == "self_update":
            new_prompt = input_data.get("new_prompt", "")
            return self.self_update_prompt(new_prompt, decision.get("reasoning", ""))

        elif action == "create_plugin":
            return self.create_custom_plugin(
                name=input_data.get("name", ""),
                version=input_data.get("version", "1.0.0"),
                description=input_data.get("description", ""),
                capabilities=input_data.get("capabilities", []),
            )

        else:
            # Standard processing
            return {
                "status": "success",
                "message": "Input processed",
                "decision": decision,
            }

    async def _handle_error(self, error: Exception, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle error with recovery.

        Args:
            error: Exception that occurred
            input_data: Input data that caused the error

        Returns:
            Error response with recovery attempt
        """
        error_msg = str(error)
        self.logger.error(f"Agent {self.name} encountered error: {error_msg}")

        # Record error
        self._record_error("processing", error_msg, input_data)

        # Attempt recovery
        recovery_result = self._attempt_recovery(error, input_data)

        return {
            "status": "error",
            "message": error_msg,
            "recovery": recovery_result,
        }

    def _record_error(self, error_type: str, error_msg: str, context: Dict[str, Any]) -> None:
        """
        Record error for learning.

        Args:
            error_type: Type of error
            error_msg: Error message
            context: Error context
        """
        error_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": error_type,
            "message": error_msg,
            "context": context,
        }

        self.error_history.append(error_record)

        # Keep only recent errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]

        self._save_context()

    def _attempt_recovery(self, error: Exception, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to recover from error.

        Args:
            error: Exception that occurred
            input_data: Input data

        Returns:
            Recovery result
        """
        # Check if similar error occurred before
        similar_errors = [
            e for e in self.error_history if e.get("message") == str(error)
        ]

        if similar_errors:
            return {
                "status": "known_error",
                "message": "Similar error occurred before",
                "occurrences": len(similar_errors),
                "suggestion": "Consider adjusting input or environment parameters",
            }
        else:
            return {
                "status": "new_error",
                "message": "First occurrence of this error",
                "suggestion": "Error recorded for future learning",
            }

    def _save_context(self) -> None:
        """Save agent context to file."""
        try:
            context_data = {
                "context": self.context.to_dict(),
                "error_history": self.error_history,
                "decision_history": self.decision_history[-100:],  # Keep last 100 decisions
            }

            with open(self.context_file, "w") as f:
                json.dump(context_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save context: {e}")

    def _load_context(self) -> None:
        """Load agent context from file."""
        try:
            if Path(self.context_file).exists():
                with open(self.context_file, "r") as f:
                    context_data = json.load(f)

                self.context.from_dict(context_data.get("context", {}))
                self.error_history = context_data.get("error_history", [])
                self.decision_history = context_data.get("decision_history", [])

                self.logger.info(f"Agent {self.name} loaded context from {self.context_file}")

        except Exception as e:
            self.logger.warning(f"Failed to load context: {e}")

    def get_learning_stats(self) -> Dict[str, Any]:
        """
        Get agent learning statistics.

        Returns:
            Learning statistics
        """
        return {
            "total_interactions": len(self.context.interactions),
            "learned_patterns": len(self.context.learned_patterns),
            "environment_params": len(self.context.environment),
            "total_errors": len(self.error_history),
            "total_decisions": len(self.decision_history),
            "capabilities": self.capabilities,
        }

