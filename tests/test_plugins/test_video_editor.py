"""
Tests for Video Editor Plugin
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

from src.plugins.video_editor import VideoEditor


@pytest.fixture
def video_editor():
    """Create VideoEditor instance"""
    editor = VideoEditor()
    editor.logger = Mock()
    editor.config = Mock()
    editor.config.get = Mock(side_effect=lambda k, d: {
        "ffmpeg_path": "ffmpeg",
        "default_codec": "libx264",
        "default_audio_codec": "aac",
        "default_quality": 23,
        "default_fps": 30,
    }.get(k, d))
    return editor


@pytest.fixture
def temp_video_file():
    """Create a temporary video file"""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        video_path = f.name
    yield video_path
    Path(video_path).unlink(missing_ok=True)


@pytest.fixture
def temp_audio_file():
    """Create a temporary audio file"""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        audio_path = f.name
    yield audio_path
    Path(audio_path).unlink(missing_ok=True)


class TestVideoEditorInit:
    """Test VideoEditor initialization"""

    def test_init(self):
        """Test plugin initialization"""
        editor = VideoEditor()
        assert editor.name == "video-editor"
        assert editor.version == "1.0.0"
        assert editor.dependencies == []
        assert editor._stats["videos_processed"] == 0
        assert "trim" in editor._stats["operations"]
        assert "concat" in editor._stats["operations"]

    def test_config_schema(self):
        """Test configuration schema"""
        editor = VideoEditor()
        assert editor.config_schema is not None
        # Check that all required fields are present
        field_names = [f.name for f in editor.config_schema.fields]
        assert "ffmpeg_path" in field_names
        assert "default_codec" in field_names
        assert "default_audio_codec" in field_names
        assert "default_quality" in field_names
        assert "default_fps" in field_names


class TestVideoEditorLifecycle:
    """Test plugin lifecycle methods"""

    @patch("subprocess.run")
    def test_on_load_success(self, mock_run, video_editor):
        """Test successful plugin load"""
        mock_run.return_value = Mock(returncode=0)
        video_editor.on_load()
        mock_run.assert_called_once()
        video_editor.logger.info.assert_called()

    @patch("subprocess.run")
    def test_on_load_ffmpeg_not_found(self, mock_run, video_editor):
        """Test plugin load when ffmpeg not found"""
        mock_run.side_effect = FileNotFoundError("ffmpeg not found")
        with pytest.raises(RuntimeError, match="ffmpeg not found"):
            video_editor.on_load()

    @patch("subprocess.run")
    def test_on_load_ffmpeg_error(self, mock_run, video_editor):
        """Test plugin load when ffmpeg returns error"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
        with pytest.raises(RuntimeError, match="ffmpeg not found"):
            video_editor.on_load()

    def test_on_unload(self, video_editor):
        """Test plugin unload"""
        video_editor._stats["videos_processed"] = 5
        video_editor.on_unload()
        video_editor.logger.info.assert_called()


class TestVideoEditorHelpers:
    """Test helper methods"""

    def test_get_config(self, video_editor):
        """Test config getter"""
        assert video_editor._get_config("ffmpeg_path", "default") == "ffmpeg"
        assert video_editor._get_config("nonexistent", "default") == "default"

    def test_get_config_no_config(self):
        """Test config getter when config is None"""
        editor = VideoEditor()
        editor.config = None
        assert editor._get_config("key", "default") == "default"

    @patch("subprocess.run")
    def test_run_ffmpeg_success(self, mock_run, video_editor):
        """Test successful ffmpeg execution"""
        mock_run.return_value = Mock(stdout="success", returncode=0)
        success, output = video_editor._run_ffmpeg(["-version"])
        assert success is True
        assert output == "success"

    @patch("subprocess.run")
    def test_run_ffmpeg_failure(self, mock_run, video_editor):
        """Test failed ffmpeg execution"""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "ffmpeg", stderr="error"
        )
        success, output = video_editor._run_ffmpeg(["-version"])
        assert success is False
        assert output == "error"

    @patch("subprocess.run")
    def test_get_video_info_success(self, mock_run, video_editor, temp_video_file):
        """Test getting video info"""
        # Create the file
        Path(temp_video_file).touch()

        mock_info = {
            "format": {"duration": "10.0"},
            "streams": [{"codec_type": "video"}]
        }
        mock_run.return_value = Mock(stdout=json.dumps(mock_info), returncode=0)

        info = video_editor.get_video_info(temp_video_file)
        assert info is not None
        assert "format" in info
        assert "streams" in info

    def test_get_video_info_file_not_found(self, video_editor):
        """Test getting info for non-existent file"""
        info = video_editor.get_video_info("/nonexistent/video.mp4")
        assert info is None

    @patch("subprocess.run")
    def test_get_video_info_ffprobe_error(self, mock_run, video_editor, temp_video_file):
        """Test getting video info when ffprobe fails"""
        Path(temp_video_file).touch()
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffprobe")

        info = video_editor.get_video_info(temp_video_file)
        assert info is None


class TestVideoEditorTrim:
    """Test video trimming"""

    def test_trim_with_duration(self, video_editor, temp_video_file):
        """Test trimming video with duration"""
        Path(temp_video_file).touch()
        output_path = temp_video_file.replace(".mp4", "_trimmed.mp4")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (True, "success")
            result = video_editor.trim(temp_video_file, output_path, start=5.0, duration=10.0)

            assert result == output_path
            assert video_editor._stats["operations"]["trim"] == 1
            assert video_editor._stats["videos_processed"] == 1
            mock_ffmpeg.assert_called_once()

        Path(output_path).unlink(missing_ok=True)

    def test_trim_with_end(self, video_editor, temp_video_file):
        """Test trimming video with end time"""
        Path(temp_video_file).touch()
        output_path = temp_video_file.replace(".mp4", "_trimmed.mp4")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (True, "success")
            result = video_editor.trim(temp_video_file, output_path, start=5.0, end=15.0)

            assert result == output_path
            assert video_editor._stats["operations"]["trim"] == 1
            mock_ffmpeg.assert_called_once()

        Path(output_path).unlink(missing_ok=True)

    def test_trim_file_not_found(self, video_editor):
        """Test trimming non-existent file"""
        with pytest.raises(FileNotFoundError):
            video_editor.trim("/nonexistent.mp4", "/output.mp4", start=0, duration=10)

    def test_trim_no_end_or_duration(self, video_editor, temp_video_file):
        """Test trimming without end or duration"""
        Path(temp_video_file).touch()
        with pytest.raises(ValueError, match="Either end or duration must be specified"):
            video_editor.trim(temp_video_file, "/output.mp4", start=0)

    def test_trim_ffmpeg_error(self, video_editor, temp_video_file):
        """Test trimming when ffmpeg fails"""
        Path(temp_video_file).touch()
        output_path = temp_video_file.replace(".mp4", "_trimmed.mp4")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (False, "error message")
            with pytest.raises(RuntimeError, match="Failed to trim video"):
                video_editor.trim(temp_video_file, output_path, start=0, duration=10)


class TestVideoEditorConcat:
    """Test video concatenation"""

    def test_concat_filter_method(self, video_editor, temp_video_file):
        """Test concatenating videos with filter method"""
        Path(temp_video_file).touch()
        video2 = temp_video_file.replace(".mp4", "_2.mp4")
        Path(video2).touch()
        output_path = temp_video_file.replace(".mp4", "_concat.mp4")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (True, "success")
            result = video_editor.concat(
                [temp_video_file, video2],
                output_path,
                method="filter"
            )

            assert result == output_path
            assert video_editor._stats["operations"]["concat"] == 1
            assert video_editor._stats["videos_processed"] == 1
            mock_ffmpeg.assert_called_once()

        Path(video2).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)

    def test_concat_demuxer_method(self, video_editor, temp_video_file):
        """Test concatenating videos with demuxer method"""
        Path(temp_video_file).touch()
        video2 = temp_video_file.replace(".mp4", "_2.mp4")
        Path(video2).touch()
        output_path = temp_video_file.replace(".mp4", "_concat.mp4")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (True, "success")
            result = video_editor.concat(
                [temp_video_file, video2],
                output_path,
                method="demuxer"
            )

            assert result == output_path
            assert video_editor._stats["operations"]["concat"] == 1
            mock_ffmpeg.assert_called_once()

        Path(video2).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)

    def test_concat_too_few_videos(self, video_editor, temp_video_file):
        """Test concatenating with less than 2 videos"""
        with pytest.raises(ValueError, match="At least 2 videos required"):
            video_editor.concat([temp_video_file], "/output.mp4")

    def test_concat_file_not_found(self, video_editor):
        """Test concatenating non-existent files"""
        with pytest.raises(FileNotFoundError):
            video_editor.concat(["/nonexistent1.mp4", "/nonexistent2.mp4"], "/output.mp4")

    def test_concat_ffmpeg_error(self, video_editor, temp_video_file):
        """Test concatenating when ffmpeg fails"""
        Path(temp_video_file).touch()
        video2 = temp_video_file.replace(".mp4", "_2.mp4")
        Path(video2).touch()

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (False, "error")
            with pytest.raises(RuntimeError, match="Failed to concatenate videos"):
                video_editor.concat([temp_video_file, video2], "/output.mp4")

        Path(video2).unlink(missing_ok=True)

    def test_concat_demuxer_ffmpeg_error(self, video_editor, temp_video_file):
        """Test concatenating with demuxer method when ffmpeg fails"""
        Path(temp_video_file).touch()
        video2 = temp_video_file.replace(".mp4", "_2.mp4")
        Path(video2).touch()

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (False, "error")
            with pytest.raises(RuntimeError, match="Failed to concatenate videos"):
                video_editor.concat([temp_video_file, video2], "/output.mp4", method="demuxer")

        Path(video2).unlink(missing_ok=True)


class TestVideoEditorConvert:
    """Test video format conversion"""

    def test_convert_format_default_settings(self, video_editor, temp_video_file):
        """Test converting video with default settings"""
        Path(temp_video_file).touch()
        output_path = temp_video_file.replace(".mp4", ".avi")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (True, "success")
            result = video_editor.convert_format(temp_video_file, output_path)

            assert result == output_path
            assert video_editor._stats["operations"]["convert"] == 1
            mock_ffmpeg.assert_called_once()

        Path(output_path).unlink(missing_ok=True)

    def test_convert_format_custom_settings(self, video_editor, temp_video_file):
        """Test converting video with custom settings"""
        Path(temp_video_file).touch()
        output_path = temp_video_file.replace(".mp4", ".avi")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (True, "success")
            result = video_editor.convert_format(
                temp_video_file,
                output_path,
                codec="libx265",
                audio_codec="mp3",
                quality=20,
                fps=60
            )

            assert result == output_path
            mock_ffmpeg.assert_called_once()

        Path(output_path).unlink(missing_ok=True)

    def test_convert_format_file_not_found(self, video_editor):
        """Test converting non-existent file"""
        with pytest.raises(FileNotFoundError):
            video_editor.convert_format("/nonexistent.mp4", "/output.avi")

    def test_convert_format_ffmpeg_error(self, video_editor, temp_video_file):
        """Test converting when ffmpeg fails"""
        Path(temp_video_file).touch()

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (False, "error")
            with pytest.raises(RuntimeError, match="Failed to convert video"):
                video_editor.convert_format(temp_video_file, "/output.avi")


class TestVideoEditorExtractAudio:
    """Test audio extraction"""

    def test_extract_audio_success(self, video_editor, temp_video_file):
        """Test extracting audio from video"""
        Path(temp_video_file).touch()
        output_path = temp_video_file.replace(".mp4", ".mp3")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (True, "success")
            result = video_editor.extract_audio(temp_video_file, output_path)

            assert result == output_path
            assert video_editor._stats["operations"]["extract_audio"] == 1
            mock_ffmpeg.assert_called_once()

        Path(output_path).unlink(missing_ok=True)

    def test_extract_audio_custom_codec(self, video_editor, temp_video_file):
        """Test extracting audio with custom codec"""
        Path(temp_video_file).touch()
        output_path = temp_video_file.replace(".mp4", ".mp3")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (True, "success")
            result = video_editor.extract_audio(temp_video_file, output_path, audio_codec="mp3")

            assert result == output_path
            mock_ffmpeg.assert_called_once()

        Path(output_path).unlink(missing_ok=True)

    def test_extract_audio_file_not_found(self, video_editor):
        """Test extracting audio from non-existent file"""
        with pytest.raises(FileNotFoundError):
            video_editor.extract_audio("/nonexistent.mp4", "/output.mp3")

    def test_extract_audio_ffmpeg_error(self, video_editor, temp_video_file):
        """Test extracting audio when ffmpeg fails"""
        Path(temp_video_file).touch()

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (False, "error")
            with pytest.raises(RuntimeError, match="Failed to extract audio"):
                video_editor.extract_audio(temp_video_file, "/output.mp3")


class TestVideoEditorAddAudio:
    """Test adding audio to video"""

    def test_add_audio_replace(self, video_editor, temp_video_file, temp_audio_file):
        """Test replacing audio in video"""
        Path(temp_video_file).touch()
        Path(temp_audio_file).touch()
        output_path = temp_video_file.replace(".mp4", "_with_audio.mp4")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (True, "success")
            result = video_editor.add_audio(
                temp_video_file,
                temp_audio_file,
                output_path,
                replace=True
            )

            assert result == output_path
            assert video_editor._stats["operations"]["add_audio"] == 1
            mock_ffmpeg.assert_called_once()

        Path(output_path).unlink(missing_ok=True)

    def test_add_audio_mix(self, video_editor, temp_video_file, temp_audio_file):
        """Test mixing audio with existing audio"""
        Path(temp_video_file).touch()
        Path(temp_audio_file).touch()
        output_path = temp_video_file.replace(".mp4", "_mixed.mp4")

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (True, "success")
            result = video_editor.add_audio(
                temp_video_file,
                temp_audio_file,
                output_path,
                replace=False
            )

            assert result == output_path
            mock_ffmpeg.assert_called_once()

        Path(output_path).unlink(missing_ok=True)

    def test_add_audio_video_not_found(self, video_editor, temp_audio_file):
        """Test adding audio when video doesn't exist"""
        Path(temp_audio_file).touch()
        with pytest.raises(FileNotFoundError, match="Video file not found"):
            video_editor.add_audio("/nonexistent.mp4", temp_audio_file, "/output.mp4")

    def test_add_audio_audio_not_found(self, video_editor, temp_video_file):
        """Test adding audio when audio doesn't exist"""
        Path(temp_video_file).touch()
        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            video_editor.add_audio(temp_video_file, "/nonexistent.mp3", "/output.mp4")

    def test_add_audio_ffmpeg_error(self, video_editor, temp_video_file, temp_audio_file):
        """Test adding audio when ffmpeg fails"""
        Path(temp_video_file).touch()
        Path(temp_audio_file).touch()

        with patch.object(video_editor, "_run_ffmpeg") as mock_ffmpeg:
            mock_ffmpeg.return_value = (False, "error")
            with pytest.raises(RuntimeError, match="Failed to add audio"):
                video_editor.add_audio(temp_video_file, temp_audio_file, "/output.mp4")


class TestVideoEditorStats:
    """Test statistics tracking"""

    def test_get_stats(self, video_editor):
        """Test getting plugin statistics"""
        video_editor._stats["videos_processed"] = 10
        video_editor._stats["operations"]["trim"] = 5
        video_editor._stats["operations"]["concat"] = 3

        stats = video_editor.get_stats()
        assert stats["videos_processed"] == 10
        assert stats["operations"]["trim"] == 5
        assert stats["operations"]["concat"] == 3

    def test_stats_immutable(self, video_editor):
        """Test that returned stats are a copy"""
        stats = video_editor.get_stats()
        stats["videos_processed"] = 999

        # Original should not be modified
        assert video_editor._stats["videos_processed"] == 0
