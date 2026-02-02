"""
Agent Manager - AI agent lifecycle management with self-update capability
"""

from typing import Dict, List, Optional, Any
import logging


class Agent:
    """Base class for all AI agents"""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        capabilities: Optional[List[str]] = None
    ) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.capabilities = capabilities or []
        self.logger = logging.getLogger(f"agent.{name}")
        self._memory: List[Dict[str, Any]] = []

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input

        Args:
            input_data: Input data from user

        Returns:
            Response data
        """
        raise NotImplementedError("Subclasses must implement process()")

    def update_prompt(self, new_prompt: str) -> None:
        """Update agent's system prompt"""
        self.system_prompt = new_prompt
        self.logger.info(f"Agent {self.name} prompt updated")

    def add_capability(self, capability: str) -> None:
        """Add a new capability to the agent"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.logger.info(f"Agent {self.name} gained capability: {capability}")

    def remove_capability(self, capability: str) -> None:
        """Remove a capability from the agent"""
        if capability in self.capabilities:
            self.capabilities.remove(capability)
            self.logger.info(f"Agent {self.name} lost capability: {capability}")


class AgentManager:
    """
    Agent Manager for AI agent lifecycle management

    Features:
    - Create/update/delete agents
    - Agent self-update via prompts
    - Environment parameterization
    - Plugin creation capabilities
    """

    def __init__(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.logger = logging.getLogger("agent_manager")

    def create_agent(
        self,
        name: str,
        system_prompt: str,
        capabilities: Optional[List[str]] = None
    ) -> Agent:
        """
        Create a new agent

        Args:
            name: Agent name
            system_prompt: System prompt for the agent
            capabilities: List of agent capabilities

        Returns:
            Created agent instance
        """
        agent = Agent(name, system_prompt, capabilities)
        self.agents[name] = agent
        self.logger.info(f"Agent {name} created")
        return agent

    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Get an agent by name

        Args:
            name: Agent name

        Returns:
            Agent instance if found, None otherwise
        """
        return self.agents.get(name)

    def update_agent(
        self,
        name: str,
        system_prompt: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> Optional[Agent]:
        """
        Update an agent

        Args:
            name: Agent name
            system_prompt: New system prompt (optional)
            capabilities: New capabilities (optional)

        Returns:
            Updated agent instance if found, None otherwise
        """
        agent = self.agents.get(name)
        if not agent:
            self.logger.warning(f"Agent {name} not found")
            return None

        if system_prompt:
            agent.update_prompt(system_prompt)

        if capabilities:
            agent.capabilities = capabilities

        self.logger.info(f"Agent {name} updated")
        return agent

    def delete_agent(self, name: str) -> bool:
        """
        Delete an agent

        Args:
            name: Agent name

        Returns:
            True if successful, False otherwise
        """
        if name in self.agents:
            del self.agents[name]
            self.logger.info(f"Agent {name} deleted")
            return True
        else:
            self.logger.warning(f"Agent {name} not found")
            return False

    def list_agents(self) -> List[str]:
        """
        List all agents

        Returns:
            List of agent names
        """
        return list(self.agents.keys())
