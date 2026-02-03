"""
WeChat Work Message Parser

Parses different types of messages from WeChat Work, including:
- Text messages
- Image messages
- Voice messages
- Video messages
- File messages
- Event messages
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageType(Enum):
    """WeChat Work message types."""

    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    FILE = "file"
    LOCATION = "location"
    LINK = "link"
    EVENT = "event"


@dataclass
class WeChatMessage:
    """WeChat Work message data structure."""

    msg_type: MessageType
    from_user: str
    to_user: str
    create_time: int
    msg_id: Optional[str] = None
    agent_id: Optional[str] = None

    # Text message
    content: Optional[str] = None

    # Media messages
    media_id: Optional[str] = None
    pic_url: Optional[str] = None
    format: Optional[str] = None

    # Location message
    location_x: Optional[float] = None
    location_y: Optional[float] = None
    scale: Optional[int] = None
    label: Optional[str] = None

    # Link message
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None

    # Event message
    event: Optional[str] = None
    event_key: Optional[str] = None

    # Raw data
    raw_data: Optional[Dict[str, Any]] = None


class WeChatMessageParser:
    """Parser for WeChat Work messages."""

    @staticmethod
    def parse_message(event_data: Dict[str, Any]) -> WeChatMessage:
        """
        Parse event data into WeChatMessage.

        Args:
            event_data: Raw event data dict

        Returns:
            Parsed WeChatMessage object

        Raises:
            ValueError: If message type is unknown
        """
        msg_type_str = event_data.get("MsgType", "").lower()

        try:
            msg_type = MessageType(msg_type_str)
        except ValueError:
            raise ValueError(f"Unknown message type: {msg_type_str}")

        # Common fields
        message = WeChatMessage(
            msg_type=msg_type,
            from_user=event_data.get("FromUserName", ""),
            to_user=event_data.get("ToUserName", ""),
            create_time=int(event_data.get("CreateTime", 0)),
            msg_id=event_data.get("MsgId"),
            agent_id=event_data.get("AgentID"),
            raw_data=event_data,
        )

        # Parse type-specific fields
        if msg_type == MessageType.TEXT:
            message.content = event_data.get("Content", "")

        elif msg_type == MessageType.IMAGE:
            message.media_id = event_data.get("MediaId", "")
            message.pic_url = event_data.get("PicUrl", "")

        elif msg_type == MessageType.VOICE:
            message.media_id = event_data.get("MediaId", "")
            message.format = event_data.get("Format", "")

        elif msg_type == MessageType.VIDEO:
            message.media_id = event_data.get("MediaId", "")
            message.format = event_data.get("ThumbMediaId", "")

        elif msg_type == MessageType.FILE:
            message.media_id = event_data.get("MediaId", "")

        elif msg_type == MessageType.LOCATION:
            message.location_x = float(event_data.get("Location_X", 0))
            message.location_y = float(event_data.get("Location_Y", 0))
            message.scale = int(event_data.get("Scale", 0))
            message.label = event_data.get("Label", "")

        elif msg_type == MessageType.LINK:
            message.title = event_data.get("Title", "")
            message.description = event_data.get("Description", "")
            message.url = event_data.get("Url", "")
            message.pic_url = event_data.get("PicUrl", "")

        elif msg_type == MessageType.EVENT:
            message.event = event_data.get("Event", "")
            message.event_key = event_data.get("EventKey", "")

        return message

    @staticmethod
    def extract_mentions(message: WeChatMessage) -> List[str]:
        """
        Extract @mentions from text message.

        Args:
            message: WeChatMessage object

        Returns:
            List of mentioned user IDs
        """
        if message.msg_type != MessageType.TEXT or not message.content:
            return []

        content = message.content

        # WeChat Work mentions format: @username
        import re

        pattern = r"@(\w+)"
        matches = re.findall(pattern, content)

        return matches

    @staticmethod
    def is_group_message(message: WeChatMessage) -> bool:
        """
        Check if message is from a group chat.

        Args:
            message: WeChatMessage object

        Returns:
            True if message is from group
        """
        # In WeChat Work, group messages have different ToUserName format
        # Group chat ID typically starts with specific prefixes
        return message.to_user.startswith("@chatroom") if message.to_user else False
