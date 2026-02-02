"""
Tests for SadTalker integration module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest
import torch

from src.models.sadtalker import SadTalkerModel


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
    checkpoint_path = os.path.join(temp_dir, "sadtalker.pth")
    Path(checkpoint_path).touch()
    return checkpoint_path


class TestSadTalkerModelInit:
    """Tests for SadTalkerModel initialization."""

    def test_init_default_params(self):
        """Test initialization with default parameters."""
        model = SadTalkerModel()
        assert model.device == "cpu"
        assert model.model_path is None
        assert model.fps == 25
        assert model.still_mode is False
        assert model.preprocess == "crop"
        assert model.expression_scale == 1.0

    def test_init_custom_params(self, model_checkpoint):
        """Test initialization with custom parameters."""
        model = SadTalkerModel(
            device="cpu",
            model_path=model_checkpoint,
            fps=30,
            still_mode=True,
            preprocess="resize",
            expression_scale=1.5,
        )
        assert model.device == "cpu"
        assert model.model_path == model_checkpoint
        assert model.fps == 30
        assert model.still_mode is True
        assert model.preprocess == "resize"
        assert model.expression_scale == 1.5

    def test_init_invalid_device(self):
        """Test initialization with invalid device."""
        with pytest.raises(ValueError, match="Invalid device"):
            SadTalkerModel(device="invalid")

    @patch("torch.cuda.is_available", return_value=False)
    def test_init_cuda_not_available(self, mock_cuda):
        """Test initialization with CUDA when not available."""
        with pytest.raises(ValueError, match="CUDA device requested but not available"):
            SadTalkerModel(device="cuda")

    def test_init_invalid_preprocess(self):
        """Test initialization with invalid preprocess method."""
        with pytest.raises(ValueError, match="Invalid preprocess"):
            SadTalkerModel(preprocess="invalid")

    def test_init_invalid_expression_scale_low(self):
        """Test initialization with expression scale too low."""
        with pytest.raises(ValueError, match="Invalid expression_scale"):
            SadTalkerModel(expression_scale=-0.1)

    def test_init_invalid_expression_scale_high(self):
        """Test initialization with expression scale too high."""
        with pytest.raises(ValueError, match="Invalid expression_scale"):
            SadTalkerModel(expression_scale=2.1)

    def test_init_model_path_not_found(self):
        """Test initialization with non-existent model path."""
        with pytest.raises(FileNotFoundError, match="Model checkpoint not found"):
            SadTalkerModel(model_path="/nonexistent/path.pth")


class TestSadTalkerModelFaceDetection:
    """Tests for face detection functionality."""

    def test_detect_faces_valid_image(self):
        """Test face detection with valid image."""
        model = SadTalkerModel()
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        faces = model.detect_faces(image)

        assert isinstance(faces, list)
        assert len(faces) > 0
        assert all(len(face) == 4 for face in faces)

    def test_detect_faces_multiple_calls(self):
        """Test face detection with multiple calls (lazy loading)."""
        model = SadTalkerModel()
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        faces1 = model.detect_faces(image)
        faces2 = model.detect_faces(image)

        assert faces1 == faces2
        assert model._face_detector is not None

    def test_detect_faces_invalid_input(self):
        """Test face detection with invalid input."""
        model = SadTalkerModel()

        with pytest.raises(ValueError, match="Image must be a numpy array"):
            model.detect_faces("not_an_array")

    def test_detect_faces_invalid_shape(self):
        """Test face detection with invalid image shape."""
        model = SadTalkerModel()
        image = np.random.randint(0, 255, (480, 640), dtype=np.uint8)

        with pytest.raises(ValueError, match="Image must be RGB with shape"):
            model.detect_faces(image)


class TestSadTalkerModelPreprocessing:
    """Tests for image preprocessing functionality."""

    def test_preprocess_image_valid(self, sample_image):
        """Test image preprocessing with valid image."""
        model = SadTalkerModel()

        image, faces = model.preprocess_image(sample_image)

        assert isinstance(image, np.ndarray)
        assert len(image.shape) == 3
        assert isinstance(faces, list)
        assert len(faces) > 0

    def test_preprocess_image_not_found(self):
        """Test image preprocessing with non-existent image."""
        model = SadTalkerModel()

        with pytest.raises(FileNotFoundError, match="Image file not found"):
            model.preprocess_image("/nonexistent/image.jpg")

    def test_preprocess_image_invalid_file(self, temp_dir):
        """Test image preprocessing with invalid image file."""
        invalid_path = os.path.join(temp_dir, "invalid.jpg")
        Path(invalid_path).write_text("not an image")

        model = SadTalkerModel()

        with pytest.raises(ValueError, match="Failed to load image"):
            model.preprocess_image(invalid_path)

    @patch.object(SadTalkerModel, "detect_faces", return_value=[])
    def test_preprocess_image_no_faces(self, mock_detect, sample_image):
        """Test image preprocessing when no faces are detected."""
        model = SadTalkerModel()

        with pytest.raises(ValueError, match="No faces detected in image"):
            model.preprocess_image(sample_image)


class TestSadTalkerModelVideoGeneration:
    """Tests for video generation functionality."""

    def test_generate_video_valid_inputs(self, sample_image, sample_audio, model_checkpoint, temp_dir):
        """Test video generation with valid inputs."""
        model = SadTalkerModel(model_path=model_checkpoint)
        output_path = os.path.join(temp_dir, "output.mp4")

        result_path = model.generate_video(sample_image, sample_audio, output_path)

        assert result_path == output_path
        assert os.path.exists(result_path)

    def test_generate_video_auto_output_path(self, sample_image, sample_audio, model_checkpoint):
        """Test video generation with automatic output path."""
        model = SadTalkerModel(model_path=model_checkpoint)

        result_path = model.generate_video(sample_image, sample_audio)

        assert os.path.exists(result_path)
        assert result_path.endswith(".mp4")

    def test_generate_video_image_not_found(self, sample_audio):
        """Test video generation with non-existent image."""
        model = SadTalkerModel()

        with pytest.raises(FileNotFoundError, match="Image file not found"):
            model.generate_video("/nonexistent/image.jpg", sample_audio)

    def test_generate_video_audio_not_found(self, sample_image):
        """Test video generation with non-existent audio."""
        model = SadTalkerModel()

        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            model.generate_video(sample_image, "/nonexistent/audio.wav")

    def test_generate_video_no_model_path(self, sample_image, sample_audio):
        """Test video generation without model path."""
        model = SadTalkerModel()

        with pytest.raises(ValueError, match="Model path not provided"):
            model.generate_video(sample_image, sample_audio)

    def test_generate_video_multiple_calls(self, sample_image, sample_audio, model_checkpoint, temp_dir):
        """Test video generation with multiple calls (lazy loading)."""
        model = SadTalkerModel(model_path=model_checkpoint)
        output_path1 = os.path.join(temp_dir, "output1.mp4")
        output_path2 = os.path.join(temp_dir, "output2.mp4")

        result_path1 = model.generate_video(sample_image, sample_audio, output_path1)
        result_path2 = model.generate_video(sample_image, sample_audio, output_path2)

        assert os.path.exists(result_path1)
        assert os.path.exists(result_path2)
        assert model._model is not None

    def test_save_video_no_frames(self, temp_dir):
        """Test saving video with no frames."""
        model = SadTalkerModel()
        output_path = os.path.join(temp_dir, "output.mp4")
        audio_path = os.path.join(temp_dir, "audio.wav")
        Path(audio_path).touch()

        with pytest.raises(ValueError, match="No frames to save"):
            model._save_video([], audio_path, output_path)


class TestSadTalkerModelCleanup:
    """Tests for resource cleanup."""

    def test_cleanup(self):
        """Test resource cleanup."""
        model = SadTalkerModel()
        model._model = "mock_model"
        model._face_detector = "mock_detector"

        model.cleanup()

        assert model._model is None
        assert model._face_detector is None

    @patch("torch.cuda.is_available", return_value=True)
    @patch("torch.cuda.empty_cache")
    def test_cleanup_with_cuda(self, mock_empty_cache, mock_cuda_available):
        """Test cleanup with CUDA cache clearing."""
        model = SadTalkerModel()

        model.cleanup()

        mock_empty_cache.assert_called_once()

