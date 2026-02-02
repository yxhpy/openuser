"""
Agent API endpoints for agent management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.agent_manager import AgentManager
from src.api.auth import get_current_user
from src.api.schemas import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentListResponse,
    ErrorResponse
)

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


def get_agent_manager() -> AgentManager:
    """Dependency to get AgentManager instance."""
    return AgentManager()


@router.post(
    "/create",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "Bad Request"}
    }
)
async def create_agent(
    request: AgentCreateRequest,
    current_user: dict = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager)
):
    """
    Create a new AI agent.

    Args:
        request: Agent creation request
        current_user: Current authenticated user
        agent_manager: AgentManager instance

    Returns:
        Created agent information
    """
    try:
        # Check if agent already exists
        existing_agent = agent_manager.get_agent(request.name)
        if existing_agent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent '{request.name}' already exists"
            )

        # Create agent
        agent = agent_manager.create_agent(
            name=request.name,
            system_prompt=request.system_prompt,
            capabilities=request.capabilities
        )

        return AgentResponse(
            name=agent.name,
            system_prompt=agent.system_prompt,
            capabilities=agent.capabilities
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get(
    "/list",
    response_model=AgentListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def list_agents(
    current_user: dict = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager)
):
    """
    List all AI agents.

    Args:
        current_user: Current authenticated user
        agent_manager: AgentManager instance

    Returns:
        List of all agents
    """
    try:
        agent_names = agent_manager.list_agents()
        agents = []
        for name in agent_names:
            agent = agent_manager.get_agent(name)
            if agent:
                agents.append(AgentResponse(
                    name=agent.name,
                    system_prompt=agent.system_prompt,
                    capabilities=agent.capabilities
                ))

        return AgentListResponse(
            agents=agents,
            total=len(agents)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get(
    "/{name}",
    response_model=AgentResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Agent not found"}
    }
)
async def get_agent(
    name: str,
    current_user: dict = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager)
):
    """
    Get agent details by name.

    Args:
        name: Agent name
        current_user: Current authenticated user
        agent_manager: AgentManager instance

    Returns:
        Agent information
    """
    agent = agent_manager.get_agent(name)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{name}' not found"
        )

    return AgentResponse(
        name=agent.name,
        system_prompt=agent.system_prompt,
        capabilities=agent.capabilities
    )


@router.put(
    "/{name}",
    response_model=AgentResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Agent not found"}
    }
)
async def update_agent(
    name: str,
    request: AgentUpdateRequest,
    current_user: dict = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager)
):
    """
    Update an existing agent.

    Args:
        name: Agent name
        request: Agent update request
        current_user: Current authenticated user
        agent_manager: AgentManager instance

    Returns:
        Updated agent information
    """
    try:
        agent = agent_manager.update_agent(
            name=name,
            system_prompt=request.system_prompt,
            capabilities=request.capabilities
        )

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{name}' not found"
            )

        return AgentResponse(
            name=agent.name,
            system_prompt=agent.system_prompt,
            capabilities=agent.capabilities
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}"
        )


@router.delete(
    "/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Agent not found"}
    }
)
async def delete_agent(
    name: str,
    current_user: dict = Depends(get_current_user),
    agent_manager: AgentManager = Depends(get_agent_manager)
):
    """
    Delete an agent.

    Args:
        name: Agent name
        current_user: Current authenticated user
        agent_manager: AgentManager instance

    Returns:
        No content on success
    """
    success = agent_manager.delete_agent(name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{name}' not found"
        )

