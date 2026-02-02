"""Feishu integration module for OpenUser.

This module provides integration with Feishu (Lark) platform, including:
- Bot client with authentication
- Webhook handler for events
- Message parsing and sending
- Interactive cards
- File upload/download
"""

from .bot import FeishuBot
from .webhook import FeishuWebhookHandler
from .message import FeishuMessageParser, FeishuMessage
from .card import FeishuCardBuilder
from .file_handler import FeishuFileHandler

__all__ = [
    "FeishuBot",
    "FeishuWebhookHandler",
    "FeishuMessageParser",
    "FeishuMessage",
    "FeishuCardBuilder",
    "FeishuFileHandler",
]
