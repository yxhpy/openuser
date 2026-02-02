"""
WeChat Work Bot Client

Provides a client for interacting with WeChat Work API, including:
- Access token management with auto-refresh
- Message sending (text, image, file, etc.)
- Bot information retrieval
"""

import time
from typing import Dict, Optional, Any
import httpx


class WeChatBot:
    """WeChat Work bot client with authentication and API management."""

    def __init__(
        self,
        corp_id: str,
        corp_secret: str,
        agent_id: str,
        base_url: str = "https://qyapi.weixin.qq.com",
    ):
        """
        Initialize WeChat Work bot.

        Args:
            corp_id: WeChat Work corporation ID
            corp_secret: WeChat Work corporation secret
            agent_id: Application agent ID
            base_url: WeChat Work API base URL
        """
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.agent_id = agent_id
        self.base_url = base_url.rstrip("/")
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._client = httpx.Client(timeout=30.0)

    def _get_access_token(self) -> str:
        """
        Get access token, refresh if expired.

        Returns:
            Access token string

        Raises:
            Exception: If token retrieval fails
        """
        # Check if token is still valid
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        # Request new token
        url = f"{self.base_url}/cgi-bin/gettoken"
        params = {"corpid": self.corp_id, "corpsecret": self.corp_secret}

        response = self._client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("errcode") != 0:
            raise Exception(
                f"Failed to get access token: {data.get('errmsg', 'Unknown error')}"
            )

        self._access_token = data["access_token"]
        # Set expiration time with 5 minute buffer
        expires_in = data.get("expires_in", 7200)
        self._token_expires_at = time.time() + expires_in - 300

        return self._access_token

    def send_message(
        self,
        touser: Optional[str] = None,
        toparty: Optional[str] = None,
        totag: Optional[str] = None,
        msgtype: str = "text",
        content: Dict[str, Any] = None,
        safe: int = 0,
    ) -> Dict[str, Any]:
        """
        Send message to users, departments, or tags.

        Args:
            touser: User IDs separated by '|' (e.g., "user1|user2")
            toparty: Department IDs separated by '|'
            totag: Tag IDs separated by '|'
            msgtype: Message type (text, image, voice, video, file, textcard, news, mpnews, markdown)
            content: Message content dict
            safe: Whether to enable safe mode (0=no, 1=yes)

        Returns:
            API response dict

        Raises:
            Exception: If message sending fails
        """
        access_token = self._get_access_token()
        url = f"{self.base_url}/cgi-bin/message/send"
        params = {"access_token": access_token}

        # Build message payload
        payload = {
            "touser": touser or "@all",
            "toparty": toparty or "",
            "totag": totag or "",
            "msgtype": msgtype,
            "agentid": self.agent_id,
            "safe": safe,
        }

        # Add message content
        if content:
            payload[msgtype] = content

        response = self._client.post(url, params=params, json=payload)
        response.raise_for_status()
        data = response.json()

        if data.get("errcode") != 0:
            raise Exception(
                f"Failed to send message: {data.get('errmsg', 'Unknown error')}"
            )

        return data

    def send_text_message(
        self,
        text: str,
        touser: Optional[str] = None,
        toparty: Optional[str] = None,
        totag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send text message.

        Args:
            text: Message text content
            touser: User IDs separated by '|'
            toparty: Department IDs separated by '|'
            totag: Tag IDs separated by '|'

        Returns:
            API response dict
        """
        content = {"content": text}
        return self.send_message(
            touser=touser, toparty=toparty, totag=totag, msgtype="text", content=content
        )

    def send_markdown_message(
        self,
        content: str,
        touser: Optional[str] = None,
        toparty: Optional[str] = None,
        totag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send markdown message.

        Args:
            content: Markdown content
            touser: User IDs separated by '|'
            toparty: Department IDs separated by '|'
            totag: Tag IDs separated by '|'

        Returns:
            API response dict
        """
        markdown_content = {"content": content}
        return self.send_message(
            touser=touser,
            toparty=toparty,
            totag=totag,
            msgtype="markdown",
            content=markdown_content,
        )

    def get_bot_info(self) -> Dict[str, Any]:
        """
        Get bot information.

        Returns:
            Bot information dict

        Raises:
            Exception: If request fails
        """
        access_token = self._get_access_token()
        url = f"{self.base_url}/cgi-bin/agent/get"
        params = {"access_token": access_token, "agentid": self.agent_id}

        response = self._client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("errcode") != 0:
            raise Exception(
                f"Failed to get bot info: {data.get('errmsg', 'Unknown error')}"
            )

        return data

    def close(self):
        """Close HTTP client."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
