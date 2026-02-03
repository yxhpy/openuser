"""Feishu message parser for different message types.

This module handles:
- Parsing different message types (text, image, file, etc.)
- Extracting message content
- Extracting user information
- Message validation
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Union


class FeishuMessageType(str, Enum):
    """Feishu message types."""

    TEXT = "text"
    POST = "post"
    IMAGE = "image"
    FILE = "file"
    AUDIO = "audio"
    MEDIA = "media"
    STICKER = "sticker"
    INTERACTIVE = "interactive"
    SHARE_CHAT = "share_chat"
    SHARE_USER = "share_user"


@dataclass
class FeishuMessage:
    """Parsed Feishu message.

    Attributes:
        message_id: Unique message ID
        message_type: Type of message
        content: Parsed message content
        sender_id: Sender's open_id
        chat_id: Chat ID where message was sent
        chat_type: Type of chat (p2p, group)
        create_time: Message creation timestamp
        mentions: List of mentioned users
        raw_content: Raw content string
    """

    message_id: str
    message_type: str
    content: Any
    sender_id: str
    chat_id: str
    chat_type: str
    create_time: str
    mentions: List[Dict[str, Any]]
    raw_content: str


class FeishuMessageParser:
    """Parser for Feishu messages.

    Handles parsing of different message types and extracting relevant information.
    """

    @staticmethod
    def parse_text_content(content_str: str) -> str:
        """Parse text message content.

        Args:
            content_str: JSON string containing text content

        Returns:
            Extracted text
        """
        try:
            content = json.loads(content_str)
            return str(content.get("text", ""))
        except json.JSONDecodeError:
            return content_str

    @staticmethod
    def parse_post_content(content_str: str) -> Dict[str, Any]:
        """Parse rich text post content.

        Args:
            content_str: JSON string containing post content

        Returns:
            Parsed post structure
        """
        try:
            content = json.loads(content_str)
            return dict(content) if isinstance(content, dict) else {"text": content_str}
        except json.JSONDecodeError:
            return {"text": content_str}

    @staticmethod
    def parse_image_content(content_str: str) -> Dict[str, str]:
        """Parse image message content.

        Args:
            content_str: JSON string containing image key

        Returns:
            Dict with image_key
        """
        try:
            content = json.loads(content_str)
            return {"image_key": content.get("image_key", "")}
        except json.JSONDecodeError:
            return {"image_key": ""}

    @staticmethod
    def parse_file_content(content_str: str) -> Dict[str, str]:
        """Parse file message content.

        Args:
            content_str: JSON string containing file key

        Returns:
            Dict with file_key and file_name
        """
        try:
            content = json.loads(content_str)
            return {
                "file_key": content.get("file_key", ""),
                "file_name": content.get("file_name", ""),
            }
        except json.JSONDecodeError:
            return {"file_key": "", "file_name": ""}

    @staticmethod
    def parse_audio_content(content_str: str) -> Dict[str, Any]:
        """Parse audio message content.

        Args:
            content_str: JSON string containing audio file key

        Returns:
            Dict with file_key and duration
        """
        try:
            content = json.loads(content_str)
            return {"file_key": content.get("file_key", ""), "duration": content.get("duration", 0)}
        except json.JSONDecodeError:
            return {"file_key": "", "duration": 0}

    def parse_content(self, message_type: str, content_str: str) -> Any:
        """Parse message content based on type.

        Args:
            message_type: Type of message
            content_str: Raw content string

        Returns:
            Parsed content
        """
        parsers: dict[str, Callable[[str], Union[str, dict[str, Any]]]] = {
            FeishuMessageType.TEXT: self.parse_text_content,
            FeishuMessageType.POST: self.parse_post_content,
            FeishuMessageType.IMAGE: self.parse_image_content,
            FeishuMessageType.FILE: self.parse_file_content,
            FeishuMessageType.AUDIO: self.parse_audio_content,
        }

        parser = parsers.get(message_type)
        if parser:
            return parser(content_str)

        # Default: try to parse as JSON
        try:
            return json.loads(content_str)
        except json.JSONDecodeError:
            return content_str

    def parse_message(self, event_data: Dict[str, Any]) -> FeishuMessage:
        """Parse message from event data.

        Args:
            event_data: Event data from webhook

        Returns:
            Parsed FeishuMessage object
        """
        message = event_data.get("message", {})
        sender = event_data.get("sender", {})

        message_id = message.get("message_id", "")
        message_type = message.get("message_type", "")
        content_str = message.get("content", "{}")
        chat_id = message.get("chat_id", "")
        chat_type = message.get("chat_type", "")
        create_time = message.get("create_time", "")
        mentions = message.get("mentions", [])

        # Parse content based on type
        content = self.parse_content(message_type, content_str)

        # Extract sender ID
        sender_id = sender.get("sender_id", {}).get("open_id", "")

        return FeishuMessage(
            message_id=message_id,
            message_type=message_type,
            content=content,
            sender_id=sender_id,
            chat_id=chat_id,
            chat_type=chat_type,
            create_time=create_time,
            mentions=mentions,
            raw_content=content_str,
        )

    def extract_mentions(self, message: FeishuMessage) -> List[str]:
        """Extract mentioned user IDs from message.

        Args:
            message: Parsed message

        Returns:
            List of mentioned user open_ids
        """
        return [
            mention.get("id", {}).get("open_id", "")
            for mention in message.mentions
            if mention.get("id", {}).get("open_id")
        ]
