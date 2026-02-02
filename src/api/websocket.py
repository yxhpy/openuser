"""
WebSocket endpoints for real-time communication.

This module provides WebSocket endpoints for:
- Real-time progress updates during video generation
- Live video streaming
- Agent communication channel
"""

from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.responses import JSONResponse
import json
import asyncio
from datetime import datetime, timezone

from src.api.auth_utils import decode_token


router = APIRouter(prefix="/api/v1/ws", tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store connections by task_id for progress updates
        self.task_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove from task connections
        for task_id in list(self.task_connections.keys()):
            self.task_connections[task_id].discard(websocket)
            if not self.task_connections[task_id]:
                del self.task_connections[task_id]

    def subscribe_to_task(self, websocket: WebSocket, task_id: str):
        """Subscribe a WebSocket to task progress updates."""
        if task_id not in self.task_connections:
            self.task_connections[task_id] = set()
        self.task_connections[task_id].add(websocket)

    def unsubscribe_from_task(self, websocket: WebSocket, task_id: str):
        """Unsubscribe a WebSocket from task progress updates."""
        if task_id in self.task_connections:
            self.task_connections[task_id].discard(websocket)
            if not self.task_connections[task_id]:
                del self.task_connections[task_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception:
            pass  # Connection might be closed

    async def broadcast_to_user(self, message: dict, user_id: str):
        """Broadcast a message to all connections of a specific user."""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)

            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection, user_id)

    async def broadcast_task_progress(self, task_id: str, progress: dict):
        """Broadcast progress update to all connections subscribed to a task."""
        if task_id in self.task_connections:
            message = {
                "type": "progress",
                "task_id": task_id,
                "data": progress,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            disconnected = set()
            for connection in self.task_connections[task_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)

            # Clean up disconnected connections
            for connection in disconnected:
                self.unsubscribe_from_task(connection, task_id)


# Global connection manager instance
manager = ConnectionManager()


async def get_current_user_ws(websocket: WebSocket, token: str = None) -> str:
    """
    Authenticate WebSocket connection using JWT token.

    Args:
        websocket: WebSocket connection
        token: JWT token from query parameter

    Returns:
        User ID if authentication successful

    Raises:
        WebSocketDisconnect: If authentication fails
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)

    payload = decode_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION)

    return user_id


@router.websocket("/progress")
async def websocket_progress(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint for real-time progress updates.

    Clients can subscribe to specific task IDs to receive progress updates.

    Message format:
    - Subscribe: {"action": "subscribe", "task_id": "task_123"}
    - Unsubscribe: {"action": "unsubscribe", "task_id": "task_123"}

    Progress updates: {"type": "progress", "task_id": "task_123", "data": {...}, "timestamp": "..."}
    """
    user_id = await get_current_user_ws(websocket, token)
    await manager.connect(websocket, user_id)

    try:
        # Send connection confirmation
        await manager.send_personal_message(
            {"type": "connected", "message": "Connected to progress updates"},
            websocket
        )

        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            action = data.get("action")
            task_id = data.get("task_id")

            if action == "subscribe" and task_id:
                manager.subscribe_to_task(websocket, task_id)
                await manager.send_personal_message(
                    {"type": "subscribed", "task_id": task_id},
                    websocket
                )
            elif action == "unsubscribe" and task_id:
                manager.unsubscribe_from_task(websocket, task_id)
                await manager.send_personal_message(
                    {"type": "unsubscribed", "task_id": task_id},
                    websocket
                )
            else:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid action or missing task_id"},
                    websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        manager.disconnect(websocket, user_id)
        raise


@router.websocket("/agent")
async def websocket_agent(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint for agent communication.

    Provides real-time bidirectional communication with AI agents.

    Message format:
    - Send to agent: {"action": "message", "agent_name": "my-agent", "content": "Hello"}
    - Agent response: {"type": "response", "agent_name": "my-agent", "content": "...", "timestamp": "..."}
    """
    user_id = await get_current_user_ws(websocket, token)
    await manager.connect(websocket, user_id)

    try:
        # Send connection confirmation
        await manager.send_personal_message(
            {"type": "connected", "message": "Connected to agent communication"},
            websocket
        )

        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "message":
                agent_name = data.get("agent_name")
                content = data.get("content")

                if not agent_name or not content:
                    await manager.send_personal_message(
                        {"type": "error", "message": "Missing agent_name or content"},
                        websocket
                    )
                    continue

                # Echo back for now (actual agent integration would go here)
                await manager.send_personal_message(
                    {
                        "type": "response",
                        "agent_name": agent_name,
                        "content": f"Agent {agent_name} received: {content}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    websocket
                )
            elif action == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()},
                    websocket
                )
            else:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid action"},
                    websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        manager.disconnect(websocket, user_id)
        raise


@router.get("/connections")
async def get_connections():
    """
    Get statistics about active WebSocket connections.

    Returns:
        Connection statistics including active users and task subscriptions
    """
    return {
        "active_users": len(manager.active_connections),
        "total_connections": sum(len(conns) for conns in manager.active_connections.values()),
        "active_task_subscriptions": len(manager.task_connections),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

