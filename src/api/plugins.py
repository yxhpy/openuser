"""
Plugin API endpoints.

This module provides REST API endpoints for managing plugins,
including listing, installing, and hot-reloading plugins.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from src.core.plugin_manager import PluginManager
from src.api.auth import get_current_user
from src.api.schemas import (
    PluginListResponse,
    PluginInstallRequest,
    PluginInstallResponse,
    PluginReloadRequest,
    PluginReloadResponse,
    ErrorResponse,
)


router = APIRouter(prefix="/api/v1/plugins", tags=["plugins"])


def get_plugin_manager():
    """Get plugin manager dependency."""
    return PluginManager()


@router.get(
    "/list",
    response_model=PluginListResponse,
    responses={401: {"model": ErrorResponse}},
    summary="List all plugins",
    description="Get a list of all loaded plugins"
)
async def list_plugins(
    current_user = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager)
):
    """
    List all loaded plugins.

    Args:
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        PluginListResponse with list of plugins
    """
    plugins = plugin_manager.list_plugins()

    return PluginListResponse(
        plugins=[
            {
                "name": plugin.name,
                "version": plugin.version,
                "dependencies": plugin.dependencies,
            }
            for plugin_name in plugins
            if (plugin := plugin_manager.get_plugin(plugin_name)) is not None
        ],
        total=len(plugins)
    )


@router.post(
    "/install",
    response_model=PluginInstallResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    summary="Install a plugin",
    description="Load and install a new plugin"
)
async def install_plugin(
    request: PluginInstallRequest,
    current_user = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager)
):
    """
    Install a plugin.

    Args:
        request: Plugin installation request
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        PluginInstallResponse with installation result
    """
    # Check if plugin already loaded
    if request.name in plugin_manager.list_plugins():
        raise HTTPException(
            status_code=400,
            detail=f"Plugin '{request.name}' is already installed"
        )

    # Load plugin
    plugin = plugin_manager.load_plugin(request.name)

    if plugin is None:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to install plugin '{request.name}'"
        )

    return PluginInstallResponse(
        name=plugin.name,
        version=plugin.version,
        message=f"Plugin '{plugin.name}' installed successfully"
    )


@router.post(
    "/reload",
    response_model=PluginReloadResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Reload a plugin",
    description="Hot-reload a plugin without system restart"
)
async def reload_plugin(
    request: PluginReloadRequest,
    current_user = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager)
):
    """
    Reload a plugin.

    Args:
        request: Plugin reload request
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        PluginReloadResponse with reload result
    """
    # Check if plugin exists
    if request.name not in plugin_manager.list_plugins():
        raise HTTPException(
            status_code=404,
            detail=f"Plugin '{request.name}' not found"
        )

    # Reload plugin
    success = plugin_manager.reload_plugin(request.name)

    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to reload plugin '{request.name}'"
        )

    plugin = plugin_manager.get_plugin(request.name)

    return PluginReloadResponse(
        name=plugin.name,
        version=plugin.version,
        message=f"Plugin '{plugin.name}' reloaded successfully"
    )
