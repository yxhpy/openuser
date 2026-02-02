"""
Tests for WeChat Work Bot Client
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from src.integrations.wechat.bot import WeChatBot


@pytest.fixture
def bot():
    """Create WeChatBot instance for testing."""
    return WeChatBot(
        corp_id="test_corp_id",
        corp_secret="test_corp_secret",
        agent_id="1000001",
    )


@pytest.fixture
def mock_response():
    """Create mock HTTP response."""
    response = Mock()
    response.raise_for_status = Mock()
    return response


class TestWeChatBot:
    """Test WeChatBot class."""

    def test_init(self, bot):
        """Test bot initialization."""
        assert bot.corp_id == "test_corp_id"
        assert bot.corp_secret == "test_corp_secret"
        assert bot.agent_id == "1000001"
        assert bot.base_url == "https://qyapi.weixin.qq.com"
        assert bot._access_token is None
        assert bot._token_expires_at == 0

    def test_init_custom_base_url(self):
        """Test bot initialization with custom base URL."""
        bot = WeChatBot(
            corp_id="test_corp_id",
            corp_secret="test_corp_secret",
            agent_id="1000001",
            base_url="https://custom.api.com/",
        )
        assert bot.base_url == "https://custom.api.com"

    @patch("httpx.Client.get")
    def test_get_access_token_success(self, mock_get, bot, mock_response):
        """Test successful access token retrieval."""
        mock_response.json.return_value = {
            "errcode": 0,
            "access_token": "test_token_123",
            "expires_in": 7200,
        }
        mock_get.return_value = mock_response

        token = bot._get_access_token()

        assert token == "test_token_123"
        assert bot._access_token == "test_token_123"
        assert bot._token_expires_at > time.time()
        mock_get.assert_called_once()

    @patch("httpx.Client.get")
    def test_get_access_token_cached(self, mock_get, bot):
        """Test access token caching."""
        # Set cached token
        bot._access_token = "cached_token"
        bot._token_expires_at = time.time() + 3600

        token = bot._get_access_token()

        assert token == "cached_token"
        mock_get.assert_not_called()

    @patch("httpx.Client.get")
    def test_get_access_token_error(self, mock_get, bot, mock_response):
        """Test access token retrieval error."""
        mock_response.json.return_value = {
            "errcode": 40013,
            "errmsg": "invalid corpid",
        }
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            bot._get_access_token()

        assert "Failed to get access token" in str(exc_info.value)
        assert "invalid corpid" in str(exc_info.value)

    @patch("httpx.Client.post")
    def test_send_message_success(self, mock_post, bot, mock_response):
        """Test successful message sending."""
        bot._access_token = "test_token"
        bot._token_expires_at = time.time() + 3600

        mock_response.json.return_value = {
            "errcode": 0,
            "errmsg": "ok",
            "msgid": "msg_123",
        }
        mock_post.return_value = mock_response

        content = {"content": "Hello, World!"}
        result = bot.send_message(
            touser="user1|user2", msgtype="text", content=content
        )

        assert result["errcode"] == 0
        assert result["msgid"] == "msg_123"
        mock_post.assert_called_once()

        # Check payload
        call_args = mock_post.call_args
        payload = call_args.kwargs["json"]
        assert payload["touser"] == "user1|user2"
        assert payload["msgtype"] == "text"
        assert payload["text"] == content
        assert payload["agentid"] == "1000001"

    @patch("httpx.Client.post")
    def test_send_message_to_all(self, mock_post, bot, mock_response):
        """Test sending message to all users."""
        bot._access_token = "test_token"
        bot._token_expires_at = time.time() + 3600

        mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_post.return_value = mock_response

        content = {"content": "Broadcast message"}
        result = bot.send_message(msgtype="text", content=content)

        payload = mock_post.call_args.kwargs["json"]
        assert payload["touser"] == "@all"

    @patch("httpx.Client.post")
    def test_send_message_error(self, mock_post, bot, mock_response):
        """Test message sending error."""
        bot._access_token = "test_token"
        bot._token_expires_at = time.time() + 3600

        mock_response.json.return_value = {
            "errcode": 40003,
            "errmsg": "invalid userid",
        }
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            bot.send_message(touser="invalid_user", msgtype="text", content={})

        assert "Failed to send message" in str(exc_info.value)
        assert "invalid userid" in str(exc_info.value)

    @patch("httpx.Client.post")
    def test_send_text_message(self, mock_post, bot, mock_response):
        """Test sending text message."""
        bot._access_token = "test_token"
        bot._token_expires_at = time.time() + 3600

        mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_post.return_value = mock_response

        result = bot.send_text_message("Hello!", touser="user1")

        payload = mock_post.call_args.kwargs["json"]
        assert payload["msgtype"] == "text"
        assert payload["text"]["content"] == "Hello!"
        assert payload["touser"] == "user1"

    @patch("httpx.Client.post")
    def test_send_markdown_message(self, mock_post, bot, mock_response):
        """Test sending markdown message."""
        bot._access_token = "test_token"
        bot._token_expires_at = time.time() + 3600

        mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_post.return_value = mock_response

        markdown_content = "# Title\n**Bold text**"
        result = bot.send_markdown_message(markdown_content, touser="user1")

        payload = mock_post.call_args.kwargs["json"]
        assert payload["msgtype"] == "markdown"
        assert payload["markdown"]["content"] == markdown_content

    @patch("httpx.Client.get")
    def test_get_bot_info_success(self, mock_get, bot, mock_response):
        """Test successful bot info retrieval."""
        bot._access_token = "test_token"
        bot._token_expires_at = time.time() + 3600

        mock_response.json.return_value = {
            "errcode": 0,
            "name": "Test Bot",
            "square_logo_url": "https://example.com/logo.png",
            "description": "Test bot description",
        }
        mock_get.return_value = mock_response

        info = bot.get_bot_info()

        assert info["name"] == "Test Bot"
        assert info["description"] == "Test bot description"
        mock_get.assert_called_once()

    @patch("httpx.Client.get")
    def test_get_bot_info_error(self, mock_get, bot, mock_response):
        """Test bot info retrieval error."""
        bot._access_token = "test_token"
        bot._token_expires_at = time.time() + 3600

        mock_response.json.return_value = {
            "errcode": 40003,
            "errmsg": "invalid agentid",
        }
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            bot.get_bot_info()

        assert "Failed to get bot info" in str(exc_info.value)

    def test_context_manager(self, bot):
        """Test context manager usage."""
        with patch.object(bot._client, "close") as mock_close:
            with bot as b:
                assert b is bot
            mock_close.assert_called_once()

    def test_close(self, bot):
        """Test client close."""
        with patch.object(bot._client, "close") as mock_close:
            bot.close()
            mock_close.assert_called_once()
