"""
Tests for WeChat Work Message Parser
"""

import pytest
from src.integrations.wechat.message import (
    WeChatMessage,
    WeChatMessageParser,
    MessageType,
)


class TestWeChatMessageParser:
    """Test WeChatMessageParser class."""

    def test_parse_text_message(self):
        """Test parsing text message."""
        event_data = {
            "MsgType": "text",
            "FromUserName": "user123",
            "ToUserName": "bot456",
            "CreateTime": "1234567890",
            "MsgId": "msg_001",
            "AgentID": "1000001",
            "Content": "Hello, bot!",
        }

        message = WeChatMessageParser.parse_message(event_data)

        assert message.msg_type == MessageType.TEXT
        assert message.from_user == "user123"
        assert message.to_user == "bot456"
        assert message.create_time == 1234567890
        assert message.msg_id == "msg_001"
        assert message.agent_id == "1000001"
        assert message.content == "Hello, bot!"

    def test_parse_image_message(self):
        """Test parsing image message."""
        event_data = {
            "MsgType": "image",
            "FromUserName": "user123",
            "ToUserName": "bot456",
            "CreateTime": "1234567890",
            "MsgId": "msg_002",
            "MediaId": "media_123",
            "PicUrl": "https://example.com/image.jpg",
        }

        message = WeChatMessageParser.parse_message(event_data)

        assert message.msg_type == MessageType.IMAGE
        assert message.media_id == "media_123"
        assert message.pic_url == "https://example.com/image.jpg"

    def test_parse_voice_message(self):
        """Test parsing voice message."""
        event_data = {
            "MsgType": "voice",
            "FromUserName": "user123",
            "ToUserName": "bot456",
            "CreateTime": "1234567890",
            "MediaId": "voice_123",
            "Format": "amr",
        }

        message = WeChatMessageParser.parse_message(event_data)

        assert message.msg_type == MessageType.VOICE
        assert message.media_id == "voice_123"
        assert message.format == "amr"

    def test_parse_video_message(self):
        """Test parsing video message."""
        event_data = {
            "MsgType": "video",
            "FromUserName": "user123",
            "ToUserName": "bot456",
            "CreateTime": "1234567890",
            "MediaId": "video_123",
            "ThumbMediaId": "thumb_123",
        }

        message = WeChatMessageParser.parse_message(event_data)

        assert message.msg_type == MessageType.VIDEO
        assert message.media_id == "video_123"
        assert message.format == "thumb_123"

    def test_parse_file_message(self):
        """Test parsing file message."""
        event_data = {
            "MsgType": "file",
            "FromUserName": "user123",
            "ToUserName": "bot456",
            "CreateTime": "1234567890",
            "MediaId": "file_123",
        }

        message = WeChatMessageParser.parse_message(event_data)

        assert message.msg_type == MessageType.FILE
        assert message.media_id == "file_123"

    def test_parse_location_message(self):
        """Test parsing location message."""
        event_data = {
            "MsgType": "location",
            "FromUserName": "user123",
            "ToUserName": "bot456",
            "CreateTime": "1234567890",
            "Location_X": "23.134521",
            "Location_Y": "113.358803",
            "Scale": "20",
            "Label": "Guangzhou",
        }

        message = WeChatMessageParser.parse_message(event_data)

        assert message.msg_type == MessageType.LOCATION
        assert message.location_x == 23.134521
        assert message.location_y == 113.358803
        assert message.scale == 20
        assert message.label == "Guangzhou"

    def test_parse_link_message(self):
        """Test parsing link message."""
        event_data = {
            "MsgType": "link",
            "FromUserName": "user123",
            "ToUserName": "bot456",
            "CreateTime": "1234567890",
            "Title": "Link Title",
            "Description": "Link description",
            "Url": "https://example.com",
            "PicUrl": "https://example.com/pic.jpg",
        }

        message = WeChatMessageParser.parse_message(event_data)

        assert message.msg_type == MessageType.LINK
        assert message.title == "Link Title"
        assert message.description == "Link description"
        assert message.url == "https://example.com"
        assert message.pic_url == "https://example.com/pic.jpg"

    def test_parse_event_message(self):
        """Test parsing event message."""
        event_data = {
            "MsgType": "event",
            "FromUserName": "user123",
            "ToUserName": "bot456",
            "CreateTime": "1234567890",
            "Event": "subscribe",
            "EventKey": "key_123",
        }

        message = WeChatMessageParser.parse_message(event_data)

        assert message.msg_type == MessageType.EVENT
        assert message.event == "subscribe"
        assert message.event_key == "key_123"

    def test_parse_unknown_message_type(self):
        """Test parsing unknown message type."""
        event_data = {
            "MsgType": "unknown_type",
            "FromUserName": "user123",
            "ToUserName": "bot456",
            "CreateTime": "1234567890",
        }

        with pytest.raises(ValueError) as exc_info:
            WeChatMessageParser.parse_message(event_data)

        assert "Unknown message type" in str(exc_info.value)

    def test_extract_mentions(self):
        """Test extracting mentions from text message."""
        message = WeChatMessage(
            msg_type=MessageType.TEXT,
            from_user="user123",
            to_user="bot456",
            create_time=1234567890,
            content="@alice @bob Hello everyone!",
        )

        mentions = WeChatMessageParser.extract_mentions(message)

        assert len(mentions) == 2
        assert "alice" in mentions
        assert "bob" in mentions

    def test_extract_mentions_no_mentions(self):
        """Test extracting mentions when there are none."""
        message = WeChatMessage(
            msg_type=MessageType.TEXT,
            from_user="user123",
            to_user="bot456",
            create_time=1234567890,
            content="Hello everyone!",
        )

        mentions = WeChatMessageParser.extract_mentions(message)

        assert len(mentions) == 0

    def test_extract_mentions_non_text_message(self):
        """Test extracting mentions from non-text message."""
        message = WeChatMessage(
            msg_type=MessageType.IMAGE,
            from_user="user123",
            to_user="bot456",
            create_time=1234567890,
        )

        mentions = WeChatMessageParser.extract_mentions(message)

        assert len(mentions) == 0

    def test_is_group_message_true(self):
        """Test detecting group message."""
        message = WeChatMessage(
            msg_type=MessageType.TEXT,
            from_user="user123",
            to_user="@chatroom123",
            create_time=1234567890,
        )

        assert WeChatMessageParser.is_group_message(message) is True

    def test_is_group_message_false(self):
        """Test detecting non-group message."""
        message = WeChatMessage(
            msg_type=MessageType.TEXT,
            from_user="user123",
            to_user="bot456",
            create_time=1234567890,
        )

        assert WeChatMessageParser.is_group_message(message) is False

    def test_raw_data_preserved(self):
        """Test that raw data is preserved in message."""
        event_data = {
            "MsgType": "text",
            "FromUserName": "user123",
            "ToUserName": "bot456",
            "CreateTime": "1234567890",
            "Content": "Test",
            "CustomField": "custom_value",
        }

        message = WeChatMessageParser.parse_message(event_data)

        assert message.raw_data == event_data
        assert message.raw_data["CustomField"] == "custom_value"
