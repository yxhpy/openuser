"""
WeChat Work File Handler

Handles file and media operations for WeChat Work, including:
- File upload (image, voice, video, file)
- File download
- Media management
"""

from pathlib import Path
from typing import Optional, Dict, Any
import httpx


class WeChatFileHandler:
    """WeChat Work file and media handler."""

    def __init__(self, bot):
        """
        Initialize file handler.

        Args:
            bot: WeChatBot instance
        """
        self.bot = bot
        self._client = httpx.Client(timeout=60.0)

    def upload_media(
        self, file_path: str, media_type: str = "file"
    ) -> Dict[str, Any]:
        """
        Upload media file to WeChat Work.

        Args:
            file_path: Path to file
            media_type: Media type (image, voice, video, file)

        Returns:
            Upload response with media_id

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If upload fails
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get file size
        file_size = file_path_obj.stat().st_size

        # Validate file size based on type
        max_sizes = {
            "image": 10 * 1024 * 1024,  # 10MB
            "voice": 2 * 1024 * 1024,  # 2MB
            "video": 10 * 1024 * 1024,  # 10MB
            "file": 20 * 1024 * 1024,  # 20MB
        }

        max_size = max_sizes.get(media_type, 20 * 1024 * 1024)
        if file_size > max_size:
            raise ValueError(
                f"File size {file_size} exceeds maximum {max_size} for {media_type}"
            )

        # Get access token
        access_token = self.bot._get_access_token()

        # Upload file
        url = f"{self.bot.base_url}/cgi-bin/media/upload"
        params = {"access_token": access_token, "type": media_type}

        with open(file_path, "rb") as f:
            files = {"media": (file_path_obj.name, f, "application/octet-stream")}
            response = self._client.post(url, params=params, files=files)

        response.raise_for_status()
        data = response.json()

        if data.get("errcode") and data["errcode"] != 0:
            raise Exception(
                f"Failed to upload media: {data.get('errmsg', 'Unknown error')}"
            )

        return data

    def download_media(self, media_id: str, output_path: str) -> str:
        """
        Download media file from WeChat Work.

        Args:
            media_id: Media ID from WeChat
            output_path: Path to save file

        Returns:
            Path to downloaded file

        Raises:
            Exception: If download fails
        """
        # Get access token
        access_token = self.bot._get_access_token()

        # Download file
        url = f"{self.bot.base_url}/cgi-bin/media/get"
        params = {"access_token": access_token, "media_id": media_id}

        response = self._client.get(url, params=params)
        response.raise_for_status()

        # Check if response is JSON (error)
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            data = response.json()
            raise Exception(
                f"Failed to download media: {data.get('errmsg', 'Unknown error')}"
            )

        # Save file
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(response.content)

        return output_path

    def upload_image(self, image_path: str) -> str:
        """
        Upload image and return media_id.

        Args:
            image_path: Path to image file

        Returns:
            Media ID

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If upload fails
        """
        result = self.upload_media(image_path, media_type="image")
        return result.get("media_id", "")

    def upload_voice(self, voice_path: str) -> str:
        """
        Upload voice and return media_id.

        Args:
            voice_path: Path to voice file

        Returns:
            Media ID

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If upload fails
        """
        result = self.upload_media(voice_path, media_type="voice")
        return result.get("media_id", "")

    def upload_video(self, video_path: str) -> str:
        """
        Upload video and return media_id.

        Args:
            video_path: Path to video file

        Returns:
            Media ID

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If upload fails
        """
        result = self.upload_media(video_path, media_type="video")
        return result.get("media_id", "")

    def upload_file(self, file_path: str) -> str:
        """
        Upload file and return media_id.

        Args:
            file_path: Path to file

        Returns:
            Media ID

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If upload fails
        """
        result = self.upload_media(file_path, media_type="file")
        return result.get("media_id", "")

    def close(self):
        """Close HTTP client."""
        self._client.close()
