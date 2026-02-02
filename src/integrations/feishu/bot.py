"""Feishu Bot client with authentication and API management.

This module provides the main Feishu bot client with:
- App authentication (app_id, app_secret)
- Access token management with auto-refresh
- API request handling
- Error handling and retries
"""

import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import httpx


class FeishuBot:
    """Feishu Bot client for API interactions.

    Handles authentication, token management, and API requests to Feishu platform.

    Attributes:
        app_id: Feishu app ID
        app_secret: Feishu app secret
        base_url: Feishu API base URL
        access_token: Current access token
        token_expires_at: Token expiration timestamp
    """

    # Feishu API endpoints
    BASE_URL = "https://open.feishu.cn/open-apis"
    TOKEN_URL = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    SEND_MESSAGE_URL = f"{BASE_URL}/im/v1/messages"

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        base_url: Optional[str] = None
    ):
        """Initialize Feishu bot client.

        Args:
            app_id: Feishu application ID
            app_secret: Feishu application secret
            base_url: Optional custom base URL for Feishu API
        """
        if not app_id or not app_secret:
            raise ValueError("app_id and app_secret are required")

        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url or self.BASE_URL
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self._client = httpx.Client(timeout=30.0)

    def __del__(self):
        """Cleanup HTTP client on deletion."""
        if hasattr(self, "_client"):
            self._client.close()

    def _get_access_token(self) -> str:
        """Get or refresh access token.

        Returns:
            Valid access token

        Raises:
            Exception: If token request fails
        """
        # Check if token is still valid (with 5 minute buffer)
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at - timedelta(minutes=5):
                return self.access_token

        # Request new token
        response = self._client.post(
            self.TOKEN_URL,
            json={
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
        )
        response.raise_for_status()

        data = response.json()
        if data.get("code") != 0:
            raise Exception(f"Failed to get access token: {data.get('msg')}")

        self.access_token = data["tenant_access_token"]
        expires_in = data.get("expire", 7200)  # Default 2 hours
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

        return self.access_token

    def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make authenticated API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: API endpoint URL
            **kwargs: Additional request parameters

        Returns:
            Response JSON data

        Raises:
            Exception: If request fails
        """
        token = self._get_access_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json"

        response = self._client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()

        data = response.json()
        if data.get("code") != 0:
            raise Exception(f"API request failed: {data.get('msg')}")

        return data

    def send_message(
        self,
        receive_id: str,
        msg_type: str,
        content: str,
        receive_id_type: str = "open_id"
    ) -> Dict[str, Any]:
        """Send message to user or group.

        Args:
            receive_id: Receiver ID (user open_id, chat_id, etc.)
            msg_type: Message type (text, post, image, etc.)
            content: Message content (JSON string)
            receive_id_type: Type of receive_id (open_id, user_id, union_id, email, chat_id)

        Returns:
            Response data with message_id

        Raises:
            Exception: If sending fails
        """
        url = f"{self.SEND_MESSAGE_URL}?receive_id_type={receive_id_type}"
        payload = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content
        }

        return self._make_request("POST", url, json=payload)

    def send_text_message(
        self,
        receive_id: str,
        text: str,
        receive_id_type: str = "open_id"
    ) -> Dict[str, Any]:
        """Send text message.

        Args:
            receive_id: Receiver ID
            text: Text content
            receive_id_type: Type of receive_id

        Returns:
            Response data with message_id
        """
        import json
        content = json.dumps({"text": text})
        return self.send_message(receive_id, "text", content, receive_id_type)

    def get_bot_info(self) -> Dict[str, Any]:
        """Get bot information.

        Returns:
            Bot information including app_id, status, etc.
        """
        url = f"{self.base_url}/bot/v3/info"
        return self._make_request("GET", url)
