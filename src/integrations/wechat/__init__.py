"""
WeChat Work Integration Module

This module provides integration with WeChat Work (企业微信) platform,
including bot client, webhook handling, message parsing, and file operations.
"""

from .bot import WeChatBot
from .webhook import WeChatWebhookHandler
from .message import WeChatMessage, WeChatMessageParser
from .card import WeChatCardBuilder
from .file_handler import WeChatFileHandler

__all__ = [
    "WeChatBot",
    "WeChatWebhookHandler",
    "WeChatMessage",
    "WeChatMessageParser",
    "WeChatCardBuilder",
    "WeChatFileHandler",
]
