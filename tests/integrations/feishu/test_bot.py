"""Tests for Feishu bot client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from src.integrations.feishu.bot import FeishuBot


class TestFeishuBot:
    """Test cases for FeishuBot."""

    def test_init_success(self):
        """Test successful initialization."""
        bot = FeishuBot(app_id="test_id", app_secret="test_secret")
        assert bot.app_id == "test_id"
        assert bot.app_secret == "test_secret"
        assert bot.access_token is None
        assert bot.token_expires_at is None

    def test_init_missing_credentials(self):
        """Test initialization with missing credentials."""
        with pytest.raises(ValueError, match="app_id and app_secret are required"):
            FeishuBot(app_id="", app_secret="test_secret")

        with pytest.raises(ValueError, match="app_id and app_secret are required"):
            FeishuBot(app_id="test_id", app_secret="")

    def test_init_custom_base_url(self):
        """Test initialization with custom base URL."""
        custom_url = "https://custom.feishu.cn/open-apis"
        bot = FeishuBot(
            app_id="test_id",
            app_secret="test_secret",
            base_url=custom_url
        )
        assert bot.base_url == custom_url

    @patch("httpx.Client.post")
    def test_get_access_token_success(self, mock_post):
        """Test successful access token retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "tenant_access_token": "test_token",
            "expire": 7200
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        bot = FeishuBot(app_id="test_id", app_secret="test_secret")
        token = bot._get_access_token()

        assert token == "test_token"
        assert bot.access_token == "test_token"
        assert bot.token_expires_at is not None

    @patch("httpx.Client.post")
    def test_get_access_token_failure(self, mock_post):
        """Test access token retrieval failure."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 99991663,
            "msg": "app access token invalid"
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        bot = FeishuBot(app_id="test_id", app_secret="test_secret")

        with pytest.raises(Exception, match="Failed to get access token"):
            bot._get_access_token()

    @patch("httpx.Client.post")
    def test_get_access_token_cached(self, mock_post):
        """Test that cached token is used when still valid."""
        bot = FeishuBot(app_id="test_id", app_secret="test_secret")
        bot.access_token = "cached_token"
        bot.token_expires_at = datetime.now() + timedelta(hours=1)

        token = bot._get_access_token()

        assert token == "cached_token"
        mock_post.assert_not_called()

    @patch("httpx.Client.post")
    def test_get_access_token_refresh_expired(self, mock_post):
        """Test token refresh when expired."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "tenant_access_token": "new_token",
            "expire": 7200
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        bot = FeishuBot(app_id="test_id", app_secret="test_secret")
        bot.access_token = "old_token"
        bot.token_expires_at = datetime.now() - timedelta(hours=1)

        token = bot._get_access_token()

        assert token == "new_token"
        mock_post.assert_called_once()

    @patch("httpx.Client.request")
    @patch.object(FeishuBot, "_get_access_token")
    def test_make_request_success(self, mock_get_token, mock_request):
        """Test successful API request."""
        mock_get_token.return_value = "test_token"
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {"result": "success"}
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        bot = FeishuBot(app_id="test_id", app_secret="test_secret")
        result = bot._make_request("GET", "https://test.url")

        assert result["code"] == 0
        assert result["data"]["result"] == "success"

    @patch("httpx.Client.request")
    @patch.object(FeishuBot, "_get_access_token")
    def test_make_request_failure(self, mock_get_token, mock_request):
        """Test API request failure."""
        mock_get_token.return_value = "test_token"
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 1001,
            "msg": "API error"
        }
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        bot = FeishuBot(app_id="test_id", app_secret="test_secret")

        with pytest.raises(Exception, match="API request failed"):
            bot._make_request("GET", "https://test.url")

    @patch.object(FeishuBot, "_make_request")
    def test_send_message_success(self, mock_make_request):
        """Test sending message."""
        mock_make_request.return_value = {
            "code": 0,
            "data": {"message_id": "msg_123"}
        }

        bot = FeishuBot(app_id="test_id", app_secret="test_secret")
        result = bot.send_message(
            receive_id="user_123",
            msg_type="text",
            content='{"text":"Hello"}',
            receive_id_type="open_id"
        )

        assert result["data"]["message_id"] == "msg_123"
        mock_make_request.assert_called_once()

    @patch.object(FeishuBot, "send_message")
    def test_send_text_message(self, mock_send_message):
        """Test sending text message."""
        mock_send_message.return_value = {
            "code": 0,
            "data": {"message_id": "msg_123"}
        }

        bot = FeishuBot(app_id="test_id", app_secret="test_secret")
        result = bot.send_text_message(
            receive_id="user_123",
            text="Hello World"
        )

        assert result["data"]["message_id"] == "msg_123"
        # Verify content is properly formatted JSON
        call_args = mock_send_message.call_args
        # Get positional and keyword arguments
        args, kwargs = call_args
        # Content should be in kwargs or as the 3rd positional argument
        content_str = kwargs.get("content") if "content" in kwargs else args[2]
        content = json.loads(content_str)
        assert content["text"] == "Hello World"

    @patch.object(FeishuBot, "_make_request")
    def test_get_bot_info(self, mock_make_request):
        """Test getting bot information."""
        mock_make_request.return_value = {
            "code": 0,
            "data": {
                "app_id": "test_id",
                "status": "active"
            }
        }

        bot = FeishuBot(app_id="test_id", app_secret="test_secret")
        result = bot.get_bot_info()

        assert result["data"]["app_id"] == "test_id"
        assert result["data"]["status"] == "active"
