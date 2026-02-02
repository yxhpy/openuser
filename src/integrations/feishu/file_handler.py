"""Feishu file handler for upload and download operations.

This module provides:
- File upload to Feishu
- File download from Feishu
- Image upload and download
- File type validation
"""

from typing import Optional, BinaryIO
from pathlib import Path
import httpx


class FeishuFileHandler:
    """Handler for Feishu file operations.

    Handles file and image upload/download with Feishu platform.

    Attributes:
        bot: FeishuBot instance for authentication
        base_url: Feishu API base URL
    """

    # File type constants
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/bmp"}
    ALLOWED_FILE_TYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "application/zip",
    }

    # Size limits (in bytes)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_FILE_SIZE = 30 * 1024 * 1024   # 30MB

    def __init__(self, bot):
        """Initialize file handler.

        Args:
            bot: FeishuBot instance for API access
        """
        self.bot = bot
        self.base_url = bot.base_url
        self._client = httpx.Client(timeout=60.0)

    def __del__(self):
        """Cleanup HTTP client on deletion."""
        if hasattr(self, "_client"):
            self._client.close()

    def upload_image(
        self,
        image_path: str,
        image_type: str = "message"
    ) -> str:
        """Upload image to Feishu.

        Args:
            image_path: Path to image file
            image_type: Image type (message, avatar)

        Returns:
            Image key for referencing the uploaded image

        Raises:
            ValueError: If file is invalid
            Exception: If upload fails
        """
        path = Path(image_path)
        if not path.exists():
            raise ValueError(f"Image file not found: {image_path}")

        # Check file size
        file_size = path.stat().st_size
        if file_size > self.MAX_IMAGE_SIZE:
            raise ValueError(f"Image size exceeds limit: {file_size} > {self.MAX_IMAGE_SIZE}")

        # Prepare request
        url = f"{self.base_url}/im/v1/images"
        token = self.bot._get_access_token()

        with open(image_path, "rb") as f:
            files = {
                "image": (path.name, f, "image/png")
            }
            data = {
                "image_type": image_type
            }
            headers = {
                "Authorization": f"Bearer {token}"
            }

            response = self._client.post(url, files=files, data=data, headers=headers)
            response.raise_for_status()

            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"Failed to upload image: {result.get('msg')}")

            return result["data"]["image_key"]

    def download_image(
        self,
        image_key: str,
        output_path: str
    ) -> str:
        """Download image from Feishu.

        Args:
            image_key: Image key from Feishu
            output_path: Path to save downloaded image

        Returns:
            Path to downloaded file

        Raises:
            Exception: If download fails
        """
        url = f"{self.base_url}/im/v1/images/{image_key}"
        token = self.bot._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = self._client.get(url, headers=headers)
        response.raise_for_status()

        # Save to file
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(response.content)

        return output_path

    def upload_file(
        self,
        file_path: str,
        file_type: str = "stream"
    ) -> str:
        """Upload file to Feishu.

        Args:
            file_path: Path to file
            file_type: File type (stream, opus, mp4, pdf, doc, xls, ppt, stream)

        Returns:
            File key for referencing the uploaded file

        Raises:
            ValueError: If file is invalid
            Exception: If upload fails
        """
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")

        # Check file size
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds limit: {file_size} > {self.MAX_FILE_SIZE}")

        # Prepare request
        url = f"{self.base_url}/im/v1/files"
        token = self.bot._get_access_token()

        with open(file_path, "rb") as f:
            files = {
                "file": (path.name, f, "application/octet-stream")
            }
            data = {
                "file_type": file_type,
                "file_name": path.name
            }
            headers = {
                "Authorization": f"Bearer {token}"
            }

            response = self._client.post(url, files=files, data=data, headers=headers)
            response.raise_for_status()

            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"Failed to upload file: {result.get('msg')}")

            return result["data"]["file_key"]

    def download_file(
        self,
        file_key: str,
        output_path: str
    ) -> str:
        """Download file from Feishu.

        Args:
            file_key: File key from Feishu
            output_path: Path to save downloaded file

        Returns:
            Path to downloaded file

        Raises:
            Exception: If download fails
        """
        url = f"{self.base_url}/im/v1/files/{file_key}"
        token = self.bot._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = self._client.get(url, headers=headers)
        response.raise_for_status()

        # Save to file
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(response.content)

        return output_path
