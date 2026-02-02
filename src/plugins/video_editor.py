"""
Video Editor Plugin

Provides video editing utilities including trimming, concatenation,
format conversion, and basic video operations using ffmpeg.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Any
import json

from src.core.plugin_manager import Plugin
from src.core.plugin_config import PluginConfigSchema, ConfigField, ConfigFieldType


class VideoEditor(Plugin):
    """Video editing plugin with ffmpeg integration"""

    name = "video-editor"
    version = "1.0.0"
    description = "Video editing utilities using ffmpeg"
    dependencies = []

    # Define configuration schema
    config_schema = PluginConfigSchema()
    config_schema.add_field(ConfigField(
        name="ffmpeg_path",
        field_type=ConfigFieldType.STRING,
        default="ffmpeg",
        description="Path to ffmpeg executable"
    ))
    config_schema.add_field(ConfigField(
        name="default_codec",
        field_type=ConfigFieldType.STRING,
        default="libx264",
        description="Default video codec"
    ))
    config_schema.add_field(ConfigField(
        name="default_audio_codec",
        field_type=ConfigFieldType.STRING,
        default="aac",
        description="Default audio codec"
    ))
    config_schema.add_field(ConfigField(
        name="default_quality",
        field_type=ConfigFieldType.INTEGER,
        default=23,
        description="Default CRF quality (0-51, lower is better)",
        validator=lambda x: 0 <= x <= 51
    ))
    config_schema.add_field(ConfigField(
        name="default_fps",
        field_type=ConfigFieldType.INTEGER,
        default=30,
        description="Default frames per second",
        validator=lambda x: x > 0
    ))

    def __init__(self):
        super().__init__()
        self._stats = {
            "videos_processed": 0,
            "total_duration": 0.0,
            "operations": {
                "trim": 0,
                "concat": 0,
                "convert": 0,
                "extract_audio": 0,
                "add_audio": 0,
            }
        }

    def _get_config(self, key: str, default: Any) -> Any:
        """Helper to get config value safely"""
        if self.config:
            return self.config.get(key, default)
        return default

    def on_load(self):
        """Called when plugin is loaded"""
        super().on_load()
        # Verify ffmpeg is available
        ffmpeg_path = self._get_config("ffmpeg_path", "ffmpeg")
        try:
            subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                check=True
            )
            self.logger.info(f"Video editor plugin loaded. ffmpeg: {ffmpeg_path}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(f"ffmpeg not found at {ffmpeg_path}: {e}")

    def on_unload(self):
        """Called when plugin is unloaded"""
        super().on_unload()
        self.logger.info(
            f"Video editor plugin unloaded. "
            f"Processed {self._stats['videos_processed']} videos"
        )

    def _run_ffmpeg(self, args: List[str]) -> Tuple[bool, str]:
        """
        Run ffmpeg command

        Args:
            args: ffmpeg arguments

        Returns:
            Tuple of (success, output/error message)
        """
        ffmpeg_path = self._get_config("ffmpeg_path", "ffmpeg")
        cmd = [ffmpeg_path] + args

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        Get video information using ffprobe

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video information or None if failed
        """
        if not Path(video_path).exists():
            return None

        ffprobe_path = self._get_config("ffmpeg_path", "ffmpeg").replace("ffmpeg", "ffprobe")

        try:
            result = subprocess.run(
                [
                    ffprobe_path,
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    video_path
                ],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            return None

    def trim(
        self,
        input_path: str,
        output_path: str,
        start: float,
        end: Optional[float] = None,
        duration: Optional[float] = None
    ) -> str:
        """
        Trim video to specified time range

        Args:
            input_path: Path to input video
            output_path: Path to output video
            start: Start time in seconds
            end: End time in seconds (optional, use duration instead)
            duration: Duration in seconds (optional, use end instead)

        Returns:
            Path to output video

        Raises:
            ValueError: If neither end nor duration is specified
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If ffmpeg command fails
        """
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if end is None and duration is None:
            raise ValueError("Either end or duration must be specified")

        # Build ffmpeg command
        args = ["-i", input_path, "-ss", str(start)]

        if duration is not None:
            args.extend(["-t", str(duration)])
        elif end is not None:
            args.extend(["-to", str(end)])

        # Add codec and quality settings
        codec = self._get_config("default_codec", "libx264")
        quality = self._get_config("default_quality", 23)
        audio_codec = self._get_config("default_audio_codec", "aac")

        args.extend([
            "-c:v", codec,
            "-crf", str(quality),
            "-c:a", audio_codec,
            "-y",  # Overwrite output file
            output_path
        ])

        success, message = self._run_ffmpeg(args)
        if not success:
            raise RuntimeError(f"Failed to trim video: {message}")

        self._stats["operations"]["trim"] += 1
        self._stats["videos_processed"] += 1

        return output_path

    def concat(
        self,
        input_paths: List[str],
        output_path: str,
        method: str = "filter"
    ) -> str:
        """
        Concatenate multiple videos

        Args:
            input_paths: List of input video paths
            output_path: Path to output video
            method: Concatenation method ("filter" or "demuxer")
                   - filter: Re-encodes videos (slower, more compatible)
                   - demuxer: Copies streams (faster, requires same format)

        Returns:
            Path to output video

        Raises:
            ValueError: If less than 2 videos provided
            FileNotFoundError: If any input file doesn't exist
            RuntimeError: If ffmpeg command fails
        """
        if len(input_paths) < 2:
            raise ValueError("At least 2 videos required for concatenation")

        for path in input_paths:
            if not Path(path).exists():
                raise FileNotFoundError(f"Input file not found: {path}")

        if method == "filter":
            # Use concat filter (re-encodes)
            filter_complex = ""
            for i in range(len(input_paths)):
                filter_complex += f"[{i}:v][{i}:a]"
            filter_complex += f"concat=n={len(input_paths)}:v=1:a=1[outv][outa]"

            args = []
            for path in input_paths:
                args.extend(["-i", path])

            codec = self.config.get("default_codec", "libx264")
            quality = self.config.get("default_quality", 23)
            audio_codec = self.config.get("default_audio_codec", "aac")

            args.extend([
                "-filter_complex", filter_complex,
                "-map", "[outv]",
                "-map", "[outa]",
                "-c:v", codec,
                "-crf", str(quality),
                "-c:a", audio_codec,
                "-y",
                output_path
            ])

        else:  # demuxer method
            # Create temporary file list
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for path in input_paths:
                    f.write(f"file '{Path(path).absolute()}'\n")
                list_file = f.name

            try:
                args = [
                    "-f", "concat",
                    "-safe", "0",
                    "-i", list_file,
                    "-c", "copy",
                    "-y",
                    output_path
                ]

                success, message = self._run_ffmpeg(args)
                if not success:
                    raise RuntimeError(f"Failed to concatenate videos: {message}")
            finally:
                Path(list_file).unlink(missing_ok=True)

            self._stats["operations"]["concat"] += 1
            self._stats["videos_processed"] += 1
            return output_path

        success, message = self._run_ffmpeg(args)
        if not success:
            raise RuntimeError(f"Failed to concatenate videos: {message}")

        self._stats["operations"]["concat"] += 1
        self._stats["videos_processed"] += 1

        return output_path

    def convert_format(
        self,
        input_path: str,
        output_path: str,
        codec: Optional[str] = None,
        audio_codec: Optional[str] = None,
        quality: Optional[int] = None,
        fps: Optional[int] = None
    ) -> str:
        """
        Convert video format

        Args:
            input_path: Path to input video
            output_path: Path to output video
            codec: Video codec (default from config)
            audio_codec: Audio codec (default from config)
            quality: CRF quality 0-51 (default from config)
            fps: Frames per second (optional)

        Returns:
            Path to output video

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If ffmpeg command fails
        """
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        codec = codec or self.config.get("default_codec", "libx264")
        audio_codec = audio_codec or self.config.get("default_audio_codec", "aac")
        quality = quality or self.config.get("default_quality", 23)

        args = [
            "-i", input_path,
            "-c:v", codec,
            "-crf", str(quality),
            "-c:a", audio_codec,
        ]

        if fps is not None:
            args.extend(["-r", str(fps)])

        args.extend(["-y", output_path])

        success, message = self._run_ffmpeg(args)
        if not success:
            raise RuntimeError(f"Failed to convert video: {message}")

        self._stats["operations"]["convert"] += 1
        self._stats["videos_processed"] += 1

        return output_path

    def extract_audio(
        self,
        input_path: str,
        output_path: str,
        audio_codec: str = "aac"
    ) -> str:
        """
        Extract audio from video

        Args:
            input_path: Path to input video
            output_path: Path to output audio file
            audio_codec: Audio codec (default: aac)

        Returns:
            Path to output audio file

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If ffmpeg command fails
        """
        if not Path(input_path).exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        args = [
            "-i", input_path,
            "-vn",  # No video
            "-c:a", audio_codec,
            "-y",
            output_path
        ]

        success, message = self._run_ffmpeg(args)
        if not success:
            raise RuntimeError(f"Failed to extract audio: {message}")

        self._stats["operations"]["extract_audio"] += 1

        return output_path

    def add_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        replace: bool = True
    ) -> str:
        """
        Add or replace audio in video

        Args:
            video_path: Path to input video
            audio_path: Path to audio file
            output_path: Path to output video
            replace: If True, replace existing audio; if False, mix with existing

        Returns:
            Path to output video

        Raises:
            FileNotFoundError: If input files don't exist
            RuntimeError: If ffmpeg command fails
        """
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        codec = self.config.get("default_codec", "libx264")
        quality = self.config.get("default_quality", 23)
        audio_codec = self.config.get("default_audio_codec", "aac")

        if replace:
            args = [
                "-i", video_path,
                "-i", audio_path,
                "-c:v", codec,
                "-crf", str(quality),
                "-c:a", audio_codec,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",  # End when shortest input ends
                "-y",
                output_path
            ]
        else:
            # Mix audio tracks
            args = [
                "-i", video_path,
                "-i", audio_path,
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest[aout]",
                "-c:v", codec,
                "-crf", str(quality),
                "-c:a", audio_codec,
                "-map", "0:v:0",
                "-map", "[aout]",
                "-y",
                output_path
            ]

        success, message = self._run_ffmpeg(args)
        if not success:
            raise RuntimeError(f"Failed to add audio: {message}")

        self._stats["operations"]["add_audio"] += 1
        self._stats["videos_processed"] += 1

        return output_path

    def get_stats(self) -> dict:
        """
        Get plugin statistics

        Returns:
            Dictionary with processing statistics
        """
        return self._stats.copy()
