"""
Tests for WeChat Work File Handler
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from src.integrations.wechat.file_handler import WeChatFileHandler
from src.integrations.wechat.bot import WeChatBot


@pytest.fixture
def bot():
    """Create mock WeChatBot instance."""
    bot = Mock(spec=WeChatBot)
    bot.base_url = "https://qyapi.weixin.qq.com"
    bot._get_access_token = Mock(return_value="test_token")
    return bot


@pytest.fixture
def file_handler(bot):
    """Create WeChatFileHandler instance."""
    return WeChatFileHandler(bot)


@pytest.fixture
def temp_file(tmp_path):
    """Create temporary test file."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content")
    return str(file_path)


class TestWeChatFileHandler:
    """Test WeChatFileHandler class."""

    def test_init(self, file_handler, bot):
        """Test file handler initialization."""
        assert file_handler.bot is bot
        assert file_handler._client is not None

    @patch("httpx.Client.post")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test data")
    def test_upload_media_success(
        self, mock_file, mock_stat, mock_exists, mock_post, file_handler
    ):
        """Test successful media upload."""
        mock_exists.return_value = True
        mock_stat.return_value = Mock(st_size=1024)

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "errcode": 0,
            "media_id": "media_123",
            "created_at": 1234567890,
        }
        mock_post.return_value = mock_response

        result = file_handler.upload_media("test.jpg", media_type="image")

        assert result["media_id"] == "media_123"
        mock_post.assert_called_once()

    @patch("pathlib.Path.exists")
    def test_upload_media_file_not_found(self, mock_exists, file_handler):
        """Test upload with non-existent file."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            file_handler.upload_media("nonexistent.jpg")

    @patch("httpx.Client.post")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_upload_media_file_too_large(
        self, mock_stat, mock_exists, mock_post, file_handler
    ):
        """Test upload with file exceeding size limit."""
        mock_exists.return_value = True
        mock_stat.return_value = Mock(st_size=50 * 1024 * 1024)  # 50MB

        with pytest.raises(ValueError) as exc_info:
            file_handler.upload_media("large_file.jpg", media_type="image")

        assert "exceeds maximum" in str(exc_info.value)

    @patch("httpx.Client.post")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test data")
    def test_upload_media_api_error(
        self, mock_file, mock_stat, mock_exists, mock_post, file_handler
    ):
        """Test upload with API error."""
        mock_exists.return_value = True
        mock_stat.return_value = Mock(st_size=1024)

        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "errcode": 40004,
            "errmsg": "invalid media type",
        }
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            file_handler.upload_media("test.jpg", media_type="invalid")

        assert "Failed to upload media" in str(exc_info.value)

    @patch("httpx.Client.get")
    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    def test_download_media_success(
        self, mock_file, mock_mkdir, mock_get, file_handler, tmp_path
    ):
        """Test successful media download."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_response.content = b"image data"
        mock_get.return_value = mock_response

        output_path = str(tmp_path / "downloaded.jpg")
        result = file_handler.download_media("media_123", output_path)

        assert result == output_path
        mock_get.assert_called_once()
        mock_file.assert_called_once()

    @patch("httpx.Client.get")
    def test_download_media_api_error(self, mock_get, file_handler, tmp_path):
        """Test download with API error."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "errcode": 40007,
            "errmsg": "invalid media_id",
        }
        mock_get.return_value = mock_response

        output_path = str(tmp_path / "downloaded.jpg")

        with pytest.raises(Exception) as exc_info:
            file_handler.download_media("invalid_media_id", output_path)

        assert "Failed to download media" in str(exc_info.value)

    @patch.object(WeChatFileHandler, "upload_media")
    def test_upload_image(self, mock_upload, file_handler):
        """Test image upload shortcut."""
        mock_upload.return_value = {"media_id": "img_123"}

        result = file_handler.upload_image("test.jpg")

        assert result == "img_123"
        mock_upload.assert_called_once_with("test.jpg", media_type="image")

    @patch.object(WeChatFileHandler, "upload_media")
    def test_upload_voice(self, mock_upload, file_handler):
        """Test voice upload shortcut."""
        mock_upload.return_value = {"media_id": "voice_123"}

        result = file_handler.upload_voice("test.amr")

        assert result == "voice_123"
        mock_upload.assert_called_once_with("test.amr", media_type="voice")

    @patch.object(WeChatFileHandler, "upload_media")
    def test_upload_video(self, mock_upload, file_handler):
        """Test video upload shortcut."""
        mock_upload.return_value = {"media_id": "video_123"}

        result = file_handler.upload_video("test.mp4")

        assert result == "video_123"
        mock_upload.assert_called_once_with("test.mp4", media_type="video")

    @patch.object(WeChatFileHandler, "upload_media")
    def test_upload_file(self, mock_upload, file_handler):
        """Test file upload shortcut."""
        mock_upload.return_value = {"media_id": "file_123"}

        result = file_handler.upload_file("test.pdf")

        assert result == "file_123"
        mock_upload.assert_called_once_with("test.pdf", media_type="file")

    def test_close(self, file_handler):
        """Test client close."""
        with patch.object(file_handler._client, "close") as mock_close:
            file_handler.close()
            mock_close.assert_called_once()
