"""Tests for Feishu file handler."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from src.integrations.feishu.file_handler import FeishuFileHandler


class TestFeishuFileHandler:
    """Test cases for FeishuFileHandler."""

    @pytest.fixture
    def mock_bot(self):
        """Create mock bot."""
        bot = Mock()
        bot.base_url = "https://open.feishu.cn/open-apis"
        bot._get_access_token = Mock(return_value="test_token")
        return bot

    @pytest.fixture
    def handler(self, mock_bot):
        """Create file handler with mock bot."""
        return FeishuFileHandler(mock_bot)

    @pytest.fixture
    def temp_image(self):
        """Create temporary image file."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
            f.write(b'fake image data')
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_init(self, mock_bot):
        """Test initialization."""
        handler = FeishuFileHandler(mock_bot)

        assert handler.bot == mock_bot
        assert handler.base_url == mock_bot.base_url

    @patch("httpx.Client.post")
    def test_upload_image_success(self, mock_post, handler, temp_image):
        """Test successful image upload."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {"image_key": "img_123"}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        image_key = handler.upload_image(temp_image)

        assert image_key == "img_123"
        mock_post.assert_called_once()

    def test_upload_image_file_not_found(self, handler):
        """Test upload with non-existent file."""
        with pytest.raises(ValueError, match="Image file not found"):
            handler.upload_image("/nonexistent/image.png")

    def test_upload_image_file_too_large(self, handler):
        """Test upload with file exceeding size limit."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
            # Create file larger than MAX_IMAGE_SIZE
            f.write(b'x' * (FeishuFileHandler.MAX_IMAGE_SIZE + 1))
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Image size exceeds limit"):
                handler.upload_image(temp_path)
        finally:
            os.unlink(temp_path)

    @patch("httpx.Client.post")
    def test_upload_image_api_failure(self, mock_post, handler, temp_image):
        """Test image upload API failure."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 1001,
            "msg": "Upload failed"
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Failed to upload image"):
            handler.upload_image(temp_image)

    @patch("httpx.Client.get")
    def test_download_image_success(self, mock_get, handler):
        """Test successful image download."""
        mock_response = Mock()
        mock_response.content = b'image data'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "downloaded.png")
            result = handler.download_image("img_123", output_path)

            assert result == output_path
            assert os.path.exists(output_path)
            with open(output_path, 'rb') as f:
                assert f.read() == b'image data'

    @patch("httpx.Client.post")
    def test_upload_file_success(self, mock_post, handler, temp_image):
        """Test successful file upload."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {"file_key": "file_123"}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        file_key = handler.upload_file(temp_image, file_type="stream")

        assert file_key == "file_123"
        mock_post.assert_called_once()

    def test_upload_file_not_found(self, handler):
        """Test file upload with non-existent file."""
        with pytest.raises(ValueError, match="File not found"):
            handler.upload_file("/nonexistent/file.pdf")

    def test_upload_file_too_large(self, handler):
        """Test file upload exceeding size limit."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            # Create file larger than MAX_FILE_SIZE
            f.write(b'x' * (FeishuFileHandler.MAX_FILE_SIZE + 1))
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="File size exceeds limit"):
                handler.upload_file(temp_path)
        finally:
            os.unlink(temp_path)

    @patch("httpx.Client.post")
    def test_upload_file_api_failure(self, mock_post, handler, temp_image):
        """Test file upload API failure."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 1001,
            "msg": "Upload failed"
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Failed to upload file"):
            handler.upload_file(temp_image)

    @patch("httpx.Client.get")
    def test_download_file_success(self, mock_get, handler):
        """Test successful file download."""
        mock_response = Mock()
        mock_response.content = b'file data'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "downloaded.pdf")
            result = handler.download_file("file_123", output_path)

            assert result == output_path
            assert os.path.exists(output_path)
            with open(output_path, 'rb') as f:
                assert f.read() == b'file data'

    @patch("httpx.Client.get")
    def test_download_file_creates_directory(self, mock_get, handler):
        """Test that download creates parent directories."""
        mock_response = Mock()
        mock_response.content = b'file data'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "subdir", "file.pdf")
            handler.download_file("file_123", output_path)

            assert os.path.exists(output_path)

    def test_constants(self):
        """Test class constants."""
        assert FeishuFileHandler.MAX_IMAGE_SIZE == 10 * 1024 * 1024
        assert FeishuFileHandler.MAX_FILE_SIZE == 30 * 1024 * 1024
        assert "image/jpeg" in FeishuFileHandler.ALLOWED_IMAGE_TYPES
        assert "application/pdf" in FeishuFileHandler.ALLOWED_FILE_TYPES

