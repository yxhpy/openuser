"""Tests for Feishu message parser."""

import pytest
import json

from src.integrations.feishu.message import (
    FeishuMessageParser,
    FeishuMessage,
    FeishuMessageType
)


class TestFeishuMessageParser:
    """Test cases for FeishuMessageParser."""

    def test_parse_text_content(self):
        """Test parsing text message content."""
        parser = FeishuMessageParser()
        content_str = '{"text":"Hello World"}'

        result = parser.parse_text_content(content_str)

        assert result == "Hello World"

    def test_parse_text_content_invalid_json(self):
        """Test parsing invalid JSON as plain text."""
        parser = FeishuMessageParser()
        content_str = "Plain text"

        result = parser.parse_text_content(content_str)

        assert result == "Plain text"

    def test_parse_post_content(self):
        """Test parsing rich text post content."""
        parser = FeishuMessageParser()
        content_str = '{"title":"Title","content":[[{"tag":"text","text":"Content"}]]}'

        result = parser.parse_post_content(content_str)

        assert result["title"] == "Title"
        assert "content" in result

    def test_parse_post_content_invalid_json(self):
        """Test parsing invalid post content."""
        parser = FeishuMessageParser()
        content_str = "Invalid JSON"

        result = parser.parse_post_content(content_str)

        assert result["text"] == "Invalid JSON"

    def test_parse_image_content(self):
        """Test parsing image message content."""
        parser = FeishuMessageParser()
        content_str = '{"image_key":"img_123"}'

        result = parser.parse_image_content(content_str)

        assert result["image_key"] == "img_123"

    def test_parse_image_content_invalid_json(self):
        """Test parsing invalid image content."""
        parser = FeishuMessageParser()
        content_str = "Invalid"

        result = parser.parse_image_content(content_str)

        assert result["image_key"] == ""

    def test_parse_file_content(self):
        """Test parsing file message content."""
        parser = FeishuMessageParser()
        content_str = '{"file_key":"file_123","file_name":"test.pdf"}'

        result = parser.parse_file_content(content_str)

        assert result["file_key"] == "file_123"
        assert result["file_name"] == "test.pdf"

    def test_parse_file_content_invalid_json(self):
        """Test parsing invalid file content."""
        parser = FeishuMessageParser()
        content_str = "Invalid"

        result = parser.parse_file_content(content_str)

        assert result["file_key"] == ""
        assert result["file_name"] == ""

    def test_parse_audio_content(self):
        """Test parsing audio message content."""
        parser = FeishuMessageParser()
        content_str = '{"file_key":"audio_123","duration":120}'

        result = parser.parse_audio_content(content_str)

        assert result["file_key"] == "audio_123"
        assert result["duration"] == 120

    def test_parse_audio_content_invalid_json(self):
        """Test parsing invalid audio content."""
        parser = FeishuMessageParser()
        content_str = "Invalid"

        result = parser.parse_audio_content(content_str)

        assert result["file_key"] == ""
        assert result["duration"] == 0

    def test_parse_content_text(self):
        """Test parsing content with text type."""
        parser = FeishuMessageParser()
        content_str = '{"text":"Hello"}'

        result = parser.parse_content(FeishuMessageType.TEXT, content_str)

        assert result == "Hello"

    def test_parse_content_image(self):
        """Test parsing content with image type."""
        parser = FeishuMessageParser()
        content_str = '{"image_key":"img_123"}'

        result = parser.parse_content(FeishuMessageType.IMAGE, content_str)

        assert result["image_key"] == "img_123"

    def test_parse_content_unknown_type(self):
        """Test parsing content with unknown type."""
        parser = FeishuMessageParser()
        content_str = '{"custom":"data"}'

        result = parser.parse_content("unknown", content_str)

        assert result["custom"] == "data"

    def test_parse_content_unknown_type_invalid_json(self):
        """Test parsing unknown type with invalid JSON."""
        parser = FeishuMessageParser()
        content_str = "Plain text"

        result = parser.parse_content("unknown", content_str)

        assert result == "Plain text"

    def test_parse_message(self):
        """Test parsing complete message from event data."""
        parser = FeishuMessageParser()
        event_data = {
            "message": {
                "message_id": "msg_123",
                "message_type": "text",
                "content": '{"text":"Hello World"}',
                "chat_id": "chat_123",
                "chat_type": "p2p",
                "create_time": "1234567890",
                "mentions": [
                    {"id": {"open_id": "user_456"}}
                ]
            },
            "sender": {
                "sender_id": {"open_id": "user_123"}
            }
        }

        message = parser.parse_message(event_data)

        assert message.message_id == "msg_123"
        assert message.message_type == "text"
        assert message.content == "Hello World"
        assert message.sender_id == "user_123"
        assert message.chat_id == "chat_123"
        assert message.chat_type == "p2p"
        assert message.create_time == "1234567890"
        assert len(message.mentions) == 1

    def test_parse_message_minimal(self):
        """Test parsing message with minimal data."""
        parser = FeishuMessageParser()
        event_data = {
            "message": {},
            "sender": {}
        }

        message = parser.parse_message(event_data)

        assert message.message_id == ""
        assert message.message_type == ""
        assert message.sender_id == ""
        assert message.chat_id == ""

    def test_extract_mentions(self):
        """Test extracting mentioned user IDs."""
        parser = FeishuMessageParser()
        message = FeishuMessage(
            message_id="msg_123",
            message_type="text",
            content="Hello",
            sender_id="user_123",
            chat_id="chat_123",
            chat_type="p2p",
            create_time="1234567890",
            mentions=[
                {"id": {"open_id": "user_456"}},
                {"id": {"open_id": "user_789"}}
            ],
            raw_content="{}"
        )

        mentioned_users = parser.extract_mentions(message)

        assert len(mentioned_users) == 2
        assert "user_456" in mentioned_users
        assert "user_789" in mentioned_users

    def test_extract_mentions_empty(self):
        """Test extracting mentions from message without mentions."""
        parser = FeishuMessageParser()
        message = FeishuMessage(
            message_id="msg_123",
            message_type="text",
            content="Hello",
            sender_id="user_123",
            chat_id="chat_123",
            chat_type="p2p",
            create_time="1234567890",
            mentions=[],
            raw_content="{}"
        )

        mentioned_users = parser.extract_mentions(message)

        assert len(mentioned_users) == 0

    def test_extract_mentions_invalid_format(self):
        """Test extracting mentions with invalid format."""
        parser = FeishuMessageParser()
        message = FeishuMessage(
            message_id="msg_123",
            message_type="text",
            content="Hello",
            sender_id="user_123",
            chat_id="chat_123",
            chat_type="p2p",
            create_time="1234567890",
            mentions=[
                {"id": {}},  # Missing open_id
                {"invalid": "format"}  # Missing id
            ],
            raw_content="{}"
        )

        mentioned_users = parser.extract_mentions(message)

        assert len(mentioned_users) == 0

