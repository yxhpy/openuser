"""
Tests for video generation pipeline module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock

import cv2
import numpy as np
import pytest

from src.models.video_generator import VideoGenerator, GenerationMode


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_image(temp_dir):
    """Create a sample test image."""
    image_path = os.path.join(temp_dir, "test_image.jpg")
    image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    cv2.imwrite(image_path, image)
    return image_path


@pytest.fixture
def sample_audio(temp_dir):
    """Create a sample test audio file."""
    audio_path = os.path.join(temp_dir, "test_audio.wav")
    Path(audio_path).touch()
    return audio_path


@pytest.fixture
def model_checkpoint(temp_dir):
    """Create a mock model checkpoint file."""
    checkpoint_path = os.path.join(temp_dir, "model.pth")
    Path(checkpoint_path).touch()
    return checkpoint_path


class TestVideoGeneratorInit:
    """Tests for VideoGenerator initialization."""

    def test_init_default_params(self):
        """Test initialization with default parameters."""
        generator = VideoGenerator()
        assert generator.device == "cpu"
        assert generator.mode == GenerationMode.LIPSYNC
        assert generator.wav2lip_model is not None
        assert generator.gfpgan_model is None
        assert generator.sadtalker_model is None

    def test_init_lipsync_mode(self, model_checkpoint):
        """Test initialization with lipsync mode."""
        generator = VideoGenerator(
            mode=GenerationMode.LIPSYNC,
            wav2lip_config={"model_path": model_checkpoint},
        )
        assert generator.mode == GenerationMode.LIPSYNC
        assert generator.wav2lip_model is not None
        assert generator.gfpgan_model is None
        assert generator.sadtalker_model is None

    def test_init_talking_head_mode(self, model_checkpoint):
        """Test initialization with talking head mode."""
        generator = VideoGenerator(
            mode=GenerationMode.TALKING_HEAD,
            sadtalker_config={"model_path": model_checkpoint},
        )
        assert generator.mode == GenerationMode.TALKING_HEAD
        assert generator.wav2lip_model is None
        assert generator.gfpgan_model is None
        assert generator.sadtalker_model is not None

    def test_init_enhanced_lipsync_mode(self, model_checkpoint):
        """Test initialization with enhanced lipsync mode."""
        generator = VideoGenerator(
            mode=GenerationMode.ENHANCED_LIPSYNC,
            wav2lip_config={"model_path": model_checkpoint},
            gfpgan_config={"model_path": model_checkpoint},
        )
        assert generator.mode == GenerationMode.ENHANCED_LIPSYNC
        assert generator.wav2lip_model is not None
        assert generator.gfpgan_model is not None
        assert generator.sadtalker_model is None

    def test_init_enhanced_talking_head_mode(self, model_checkpoint):
        """Test initialization with enhanced talking head mode."""
        generator = VideoGenerator(
            mode=GenerationMode.ENHANCED_TALKING_HEAD,
            sadtalker_config={"model_path": model_checkpoint},
            gfpgan_config={"model_path": model_checkpoint},
        )
        assert generator.mode == GenerationMode.ENHANCED_TALKING_HEAD
        assert generator.wav2lip_model is None
        assert generator.gfpgan_model is not None
        assert generator.sadtalker_model is not None

    def test_init_invalid_mode(self):
        """Test initialization with invalid mode."""
        with pytest.raises(ValueError, match="Invalid mode"):
            VideoGenerator(mode="invalid")


class TestVideoGeneratorFromText:
    """Tests for text-to-video generation."""

    def test_generate_from_text_no_voice_synthesizer(self, sample_image):
        """Test text generation without voice synthesizer."""
        generator = VideoGenerator()

        with pytest.raises(ValueError, match="Voice synthesizer not initialized"):
            generator.generate_from_text("Hello", sample_image)

    def test_generate_from_text_image_not_found(self):
        """Test text generation with non-existent image."""
        generator = VideoGenerator()
        generator.voice_synthesizer = Mock()

        with pytest.raises(FileNotFoundError, match="Image file not found"):
            generator.generate_from_text("Hello", "/nonexistent/image.jpg")

    @patch("os.remove")
    def test_generate_from_text_success(self, mock_remove, sample_image, sample_audio, model_checkpoint, temp_dir):
        """Test successful text-to-video generation."""
        generator = VideoGenerator(
            mode=GenerationMode.LIPSYNC,
            wav2lip_config={"model_path": model_checkpoint},
        )

        mock_synthesizer = Mock()
        mock_synthesizer.synthesize.return_value = sample_audio
        generator.voice_synthesizer = mock_synthesizer

        output_path = os.path.join(temp_dir, "output.mp4")
        result_path = generator.generate_from_text("Hello", sample_image, output_path)

        assert os.path.exists(result_path)
        mock_synthesizer.synthesize.assert_called_once()


class TestVideoGeneratorFromAudio:
    """Tests for audio-to-video generation."""

    def test_generate_from_audio_image_not_found(self, sample_audio):
        """Test audio generation with non-existent image."""
        generator = VideoGenerator()

        with pytest.raises(FileNotFoundError, match="Image file not found"):
            generator.generate_from_audio("/nonexistent/image.jpg", sample_audio)

    def test_generate_from_audio_audio_not_found(self, sample_image):
        """Test audio generation with non-existent audio."""
        generator = VideoGenerator()

        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            generator.generate_from_audio(sample_image, "/nonexistent/audio.wav")

    def test_generate_from_audio_lipsync_mode(self, sample_image, sample_audio, model_checkpoint, temp_dir):
        """Test audio generation with lipsync mode."""
        generator = VideoGenerator(
            mode=GenerationMode.LIPSYNC,
            wav2lip_config={"model_path": model_checkpoint},
        )

        output_path = os.path.join(temp_dir, "output.mp4")
        result_path = generator.generate_from_audio(sample_image, sample_audio, output_path)

        assert os.path.exists(result_path)

    def test_generate_from_audio_talking_head_mode(self, sample_image, sample_audio, model_checkpoint, temp_dir):
        """Test audio generation with talking head mode."""
        generator = VideoGenerator(
            mode=GenerationMode.TALKING_HEAD,
            sadtalker_config={"model_path": model_checkpoint},
        )

        output_path = os.path.join(temp_dir, "output.mp4")
        result_path = generator.generate_from_audio(sample_image, sample_audio, output_path)

        assert os.path.exists(result_path)

    def test_generate_from_audio_enhanced_lipsync_mode(self, sample_image, sample_audio, model_checkpoint, temp_dir):
        """Test audio generation with enhanced lipsync mode."""
        generator = VideoGenerator(
            mode=GenerationMode.ENHANCED_LIPSYNC,
            wav2lip_config={"model_path": model_checkpoint},
            gfpgan_config={"model_path": model_checkpoint},
        )

        output_path = os.path.join(temp_dir, "output.mp4")
        result_path = generator.generate_from_audio(sample_image, sample_audio, output_path)

        assert os.path.exists(result_path)

    def test_generate_from_audio_enhanced_talking_head_mode(self, sample_image, sample_audio, model_checkpoint, temp_dir):
        """Test audio generation with enhanced talking head mode."""
        generator = VideoGenerator(
            mode=GenerationMode.ENHANCED_TALKING_HEAD,
            sadtalker_config={"model_path": model_checkpoint},
            gfpgan_config={"model_path": model_checkpoint},
        )

        output_path = os.path.join(temp_dir, "output.mp4")
        result_path = generator.generate_from_audio(sample_image, sample_audio, output_path)

        assert os.path.exists(result_path)

    def test_generate_from_audio_auto_output_path(self, sample_image, sample_audio, model_checkpoint):
        """Test audio generation with automatic output path."""
        generator = VideoGenerator(
            mode=GenerationMode.LIPSYNC,
            wav2lip_config={"model_path": model_checkpoint},
        )

        result_path = generator.generate_from_audio(sample_image, sample_audio)

        assert os.path.exists(result_path)
        assert result_path.endswith(".mp4")

    def test_generate_from_audio_unsupported_mode(self, sample_image, sample_audio):
        """Test audio generation with unsupported mode (should never happen)."""
        generator = VideoGenerator()
        generator.mode = "unsupported"

        with pytest.raises(ValueError, match="Unsupported mode"):
            generator.generate_from_audio(sample_image, sample_audio)


class TestVideoGeneratorPrivateMethods:
    """Tests for private generation methods."""

    def test_generate_lipsync_no_model(self, sample_image, sample_audio):
        """Test lipsync generation without model."""
        generator = VideoGenerator(mode=GenerationMode.TALKING_HEAD)

        with pytest.raises(ValueError, match="Wav2Lip model not initialized"):
            generator._generate_lipsync(sample_image, sample_audio, "output.mp4")

    def test_generate_talking_head_no_model(self, sample_image, sample_audio):
        """Test talking head generation without model."""
        generator = VideoGenerator(mode=GenerationMode.LIPSYNC)

        with pytest.raises(ValueError, match="SadTalker model not initialized"):
            generator._generate_talking_head(sample_image, sample_audio, "output.mp4")

    def test_generate_enhanced_lipsync_no_wav2lip(self, sample_image, sample_audio, model_checkpoint):
        """Test enhanced lipsync without Wav2Lip model."""
        generator = VideoGenerator(
            mode=GenerationMode.TALKING_HEAD,
            sadtalker_config={"model_path": model_checkpoint},
        )

        with pytest.raises(ValueError, match="Wav2Lip model not initialized"):
            generator._generate_enhanced_lipsync(sample_image, sample_audio, "output.mp4")

    def test_generate_enhanced_lipsync_no_gfpgan(self, sample_image, sample_audio, model_checkpoint):
        """Test enhanced lipsync without GFPGAN model."""
        generator = VideoGenerator(
            mode=GenerationMode.LIPSYNC,
            wav2lip_config={"model_path": model_checkpoint},
        )

        with pytest.raises(ValueError, match="GFPGAN model not initialized"):
            generator._generate_enhanced_lipsync(sample_image, sample_audio, "output.mp4")

    def test_generate_enhanced_talking_head_no_sadtalker(self, sample_image, sample_audio, model_checkpoint):
        """Test enhanced talking head without SadTalker model."""
        generator = VideoGenerator(
            mode=GenerationMode.LIPSYNC,
            wav2lip_config={"model_path": model_checkpoint},
        )

        with pytest.raises(ValueError, match="SadTalker model not initialized"):
            generator._generate_enhanced_talking_head(sample_image, sample_audio, "output.mp4")

    def test_generate_enhanced_talking_head_no_gfpgan(self, sample_image, sample_audio, model_checkpoint):
        """Test enhanced talking head without GFPGAN model."""
        generator = VideoGenerator(
            mode=GenerationMode.TALKING_HEAD,
            sadtalker_config={"model_path": model_checkpoint},
        )

        with pytest.raises(ValueError, match="GFPGAN model not initialized"):
            generator._generate_enhanced_talking_head(sample_image, sample_audio, "output.mp4")


class TestVideoGeneratorCleanup:
    """Tests for resource cleanup."""

    def test_cleanup_all_models(self, model_checkpoint):
        """Test cleanup with all models initialized."""
        generator = VideoGenerator(
            mode=GenerationMode.ENHANCED_TALKING_HEAD,
            sadtalker_config={"model_path": model_checkpoint},
            gfpgan_config={"model_path": model_checkpoint},
        )

        generator.voice_synthesizer = Mock()
        generator.cleanup()

        generator.voice_synthesizer.cleanup.assert_called_once()

    def test_cleanup_no_models(self):
        """Test cleanup with no models initialized."""
        generator = VideoGenerator()
        generator.wav2lip_model = None

        generator.cleanup()

    def test_cleanup_with_wav2lip(self, model_checkpoint):
        """Test cleanup with Wav2Lip model."""
        generator = VideoGenerator(
            mode=GenerationMode.LIPSYNC,
            wav2lip_config={"model_path": model_checkpoint},
        )

        generator.cleanup()

