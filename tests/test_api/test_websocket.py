"""
Tests for WebSocket endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime, timedelta

from src.api.main import create_app
from src.api.websocket import ConnectionManager, manager, get_current_user_ws
from src.api.auth_utils import create_access_token


@pytest.fixture
def app():
    """Create test FastAPI application."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def valid_token():
    """Create a valid JWT token for testing."""
    return create_access_token({"sub": "test_user"})


@pytest.fixture
def connection_manager():
    """Create a fresh ConnectionManager instance for testing."""
    return ConnectionManager()


class TestConnectionManager:
    """Tests for ConnectionManager class."""

    @pytest.mark.asyncio
    async def test_connect(self, connection_manager):
        """Test connecting a WebSocket."""
        websocket = AsyncMock()
        user_id = "test_user"

        await connection_manager.connect(websocket, user_id)

        websocket.accept.assert_called_once()
        assert user_id in connection_manager.active_connections
        assert websocket in connection_manager.active_connections[user_id]

    def test_disconnect(self, connection_manager):
        """Test disconnecting a WebSocket."""
        websocket = Mock()
        user_id = "test_user"

        # Add connection first
        connection_manager.active_connections[user_id] = {websocket}

        # Disconnect
        connection_manager.disconnect(websocket, user_id)

        assert user_id not in connection_manager.active_connections

    def test_disconnect_removes_from_task_connections(self, connection_manager):
        """Test that disconnect removes WebSocket from task connections."""
        websocket = Mock()
        user_id = "test_user"
        task_id = "task_123"

        # Add to both active and task connections
        connection_manager.active_connections[user_id] = {websocket}
        connection_manager.task_connections[task_id] = {websocket}

        # Disconnect
        connection_manager.disconnect(websocket, user_id)

        assert user_id not in connection_manager.active_connections
        assert task_id not in connection_manager.task_connections

    def test_subscribe_to_task(self, connection_manager):
        """Test subscribing to task updates."""
        websocket = Mock()
        task_id = "task_123"

        connection_manager.subscribe_to_task(websocket, task_id)

        assert task_id in connection_manager.task_connections
        assert websocket in connection_manager.task_connections[task_id]

    def test_unsubscribe_from_task(self, connection_manager):
        """Test unsubscribing from task updates."""
        websocket = Mock()
        task_id = "task_123"

        # Subscribe first
        connection_manager.task_connections[task_id] = {websocket}

        # Unsubscribe
        connection_manager.unsubscribe_from_task(websocket, task_id)

        assert task_id not in connection_manager.task_connections

    @pytest.mark.asyncio
    async def test_send_personal_message(self, connection_manager):
        """Test sending a personal message."""
        websocket = AsyncMock()
        message = {"type": "test", "data": "hello"}

        await connection_manager.send_personal_message(message, websocket)

        websocket.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_send_personal_message_handles_exception(self, connection_manager):
        """Test that send_personal_message handles exceptions gracefully."""
        websocket = AsyncMock()
        websocket.send_json.side_effect = Exception("Connection closed")
        message = {"type": "test"}

        # Should not raise exception
        await connection_manager.send_personal_message(message, websocket)

    @pytest.mark.asyncio
    async def test_broadcast_to_user(self, connection_manager):
        """Test broadcasting to all user connections."""
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()
        user_id = "test_user"
        message = {"type": "broadcast", "data": "hello"}

        connection_manager.active_connections[user_id] = {websocket1, websocket2}

        await connection_manager.broadcast_to_user(message, user_id)

        websocket1.send_json.assert_called_once_with(message)
        websocket2.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_to_user_cleans_up_disconnected(self, connection_manager):
        """Test that broadcast cleans up disconnected connections."""
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()
        websocket2.send_json.side_effect = Exception("Connection closed")
        user_id = "test_user"
        message = {"type": "broadcast"}

        connection_manager.active_connections[user_id] = {websocket1, websocket2}

        await connection_manager.broadcast_to_user(message, user_id)

        # websocket2 should be removed
        assert websocket2 not in connection_manager.active_connections[user_id]
        assert websocket1 in connection_manager.active_connections[user_id]

    @pytest.mark.asyncio
    async def test_broadcast_task_progress(self, connection_manager):
        """Test broadcasting task progress."""
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()
        task_id = "task_123"
        progress = {"percent": 50, "status": "processing"}

        connection_manager.task_connections[task_id] = {websocket1, websocket2}

        await connection_manager.broadcast_task_progress(task_id, progress)

        # Both websockets should receive the message
        assert websocket1.send_json.call_count == 1
        assert websocket2.send_json.call_count == 1

        # Check message structure
        call_args = websocket1.send_json.call_args[0][0]
        assert call_args["type"] == "progress"
        assert call_args["task_id"] == task_id
        assert call_args["data"] == progress
        assert "timestamp" in call_args

    @pytest.mark.asyncio
    async def test_broadcast_task_progress_cleans_up_disconnected(self, connection_manager):
        """Test that broadcast_task_progress cleans up disconnected connections."""
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()
        websocket2.send_json.side_effect = Exception("Connection closed")
        task_id = "task_123"
        progress = {"percent": 50}

        connection_manager.task_connections[task_id] = {websocket1, websocket2}

        await connection_manager.broadcast_task_progress(task_id, progress)

        # websocket2 should be removed
        assert websocket2 not in connection_manager.task_connections[task_id]
        assert websocket1 in connection_manager.task_connections[task_id]


class TestWebSocketAuthentication:
    """Tests for WebSocket authentication."""

    @pytest.mark.asyncio
    async def test_get_current_user_ws_success(self, valid_token):
        """Test successful WebSocket authentication."""
        websocket = AsyncMock()

        user_id = await get_current_user_ws(websocket, valid_token)

        assert user_id == "test_user"
        websocket.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_current_user_ws_no_token(self):
        """Test WebSocket authentication without token."""
        websocket = AsyncMock()

        with pytest.raises(Exception):  # WebSocketDisconnect
            await get_current_user_ws(websocket, None)

        websocket.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_user_ws_invalid_token(self):
        """Test WebSocket authentication with invalid token."""
        websocket = AsyncMock()

        with pytest.raises(Exception):  # WebSocketDisconnect
            await get_current_user_ws(websocket, "invalid_token")

        websocket.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_user_ws_token_without_sub(self):
        """Test WebSocket authentication with token missing 'sub' claim."""
        websocket = AsyncMock()
        token = create_access_token({"user": "test_user"})  # Missing 'sub'

        with pytest.raises(Exception):  # WebSocketDisconnect
            await get_current_user_ws(websocket, token)

        websocket.close.assert_called_once()


class TestWebSocketEndpoints:
    """Tests for WebSocket endpoints."""

    def test_websocket_progress_connection(self, client, valid_token):
        """Test WebSocket progress endpoint connection."""
        with client.websocket_connect(f"/api/v1/ws/progress?token={valid_token}") as websocket:
            # Should receive connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert "message" in data

    def test_websocket_progress_subscribe(self, client, valid_token):
        """Test subscribing to task progress."""
        with client.websocket_connect(f"/api/v1/ws/progress?token={valid_token}") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Subscribe to task
            websocket.send_json({"action": "subscribe", "task_id": "task_123"})

            # Should receive subscription confirmation
            data = websocket.receive_json()
            assert data["type"] == "subscribed"
            assert data["task_id"] == "task_123"

    def test_websocket_progress_unsubscribe(self, client, valid_token):
        """Test unsubscribing from task progress."""
        with client.websocket_connect(f"/api/v1/ws/progress?token={valid_token}") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Subscribe first
            websocket.send_json({"action": "subscribe", "task_id": "task_123"})
            websocket.receive_json()

            # Unsubscribe
            websocket.send_json({"action": "unsubscribe", "task_id": "task_123"})

            # Should receive unsubscription confirmation
            data = websocket.receive_json()
            assert data["type"] == "unsubscribed"
            assert data["task_id"] == "task_123"

    def test_websocket_progress_invalid_action(self, client, valid_token):
        """Test invalid action on progress endpoint."""
        with client.websocket_connect(f"/api/v1/ws/progress?token={valid_token}") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Send invalid action
            websocket.send_json({"action": "invalid"})

            # Should receive error
            data = websocket.receive_json()
            assert data["type"] == "error"

    def test_websocket_progress_missing_task_id(self, client, valid_token):
        """Test subscribe without task_id."""
        with client.websocket_connect(f"/api/v1/ws/progress?token={valid_token}") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Subscribe without task_id
            websocket.send_json({"action": "subscribe"})

            # Should receive error
            data = websocket.receive_json()
            assert data["type"] == "error"

    def test_websocket_agent_connection(self, client, valid_token):
        """Test WebSocket agent endpoint connection."""
        with client.websocket_connect(f"/api/v1/ws/agent?token={valid_token}") as websocket:
            # Should receive connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert "message" in data

    def test_websocket_agent_message(self, client, valid_token):
        """Test sending message to agent."""
        with client.websocket_connect(f"/api/v1/ws/agent?token={valid_token}") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Send message to agent
            websocket.send_json({
                "action": "message",
                "agent_name": "test-agent",
                "content": "Hello agent"
            })

            # Should receive response
            data = websocket.receive_json()
            assert data["type"] == "response"
            assert data["agent_name"] == "test-agent"
            assert "content" in data
            assert "timestamp" in data

    def test_websocket_agent_ping(self, client, valid_token):
        """Test ping/pong on agent endpoint."""
        with client.websocket_connect(f"/api/v1/ws/agent?token={valid_token}") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Send ping
            websocket.send_json({"action": "ping"})

            # Should receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
            assert "timestamp" in data

    def test_websocket_agent_invalid_action(self, client, valid_token):
        """Test invalid action on agent endpoint."""
        with client.websocket_connect(f"/api/v1/ws/agent?token={valid_token}") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Send invalid action
            websocket.send_json({"action": "invalid"})

            # Should receive error
            data = websocket.receive_json()
            assert data["type"] == "error"

    def test_websocket_agent_missing_fields(self, client, valid_token):
        """Test message without required fields."""
        with client.websocket_connect(f"/api/v1/ws/agent?token={valid_token}") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Send message without agent_name
            websocket.send_json({"action": "message", "content": "Hello"})

            # Should receive error
            data = websocket.receive_json()
            assert data["type"] == "error"

    def test_websocket_without_token(self, client):
        """Test WebSocket connection without authentication token."""
        with pytest.raises(Exception):  # Should fail to connect
            with client.websocket_connect("/api/v1/ws/progress"):
                pass

    def test_get_connections_endpoint(self, client):
        """Test getting connection statistics."""
        response = client.get("/api/v1/ws/connections")

        assert response.status_code == 200
        data = response.json()
        assert "active_users" in data
        assert "total_connections" in data
        assert "active_task_subscriptions" in data
        assert "timestamp" in data

    def test_websocket_progress_exception_handling(self, client, valid_token):
        """Test exception handling in progress endpoint."""
        with client.websocket_connect(f"/api/v1/ws/progress?token={valid_token}") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Send valid subscribe
            websocket.send_json({"action": "subscribe", "task_id": "task_123"})
            websocket.receive_json()

            # Close connection abruptly to trigger exception handling
            # The disconnect should be handled gracefully

    def test_websocket_agent_exception_handling(self, client, valid_token):
        """Test exception handling in agent endpoint."""
        with client.websocket_connect(f"/api/v1/ws/agent?token={valid_token}") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Send valid message
            websocket.send_json({
                "action": "message",
                "agent_name": "test-agent",
                "content": "Hello"
            })
            websocket.receive_json()

            # Close connection abruptly to trigger exception handling
            # The disconnect should be handled gracefully

