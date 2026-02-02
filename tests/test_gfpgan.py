"""
Tests for GFPGAN integration module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest
import torch

from src.models.gfpgan import GFPGANModel


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
def sample_video(temp_dir):
    """Create a sample test video."""
    video_path = os.path.join(temp_dir, "test_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, 25, (640, 480))

    for _ in range(10):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        out.write(frame)

    out.release()
    return video_path


@pytest.fixture
def model_checkpoint(temp_dir):
    """Create a mock model checkpoint file."""
    checkpoint_path = os.path.join(temp_dir, "gfpgan.pth")
    Path(checkpoint_path).touch()
    return checkpoint_path


class TestGFPGANModelInit:
    """Tests for GFPGANModel initialization."""

    def test_init_default_params(self):
        """Test initialization with default parameters."""
        model = GFPGANModel()
        assert model.device == "cpu"
        assert model.model_path is None
        assert model.upscale_factor == 2
        assert model.bg_upsampler is None
        assert model.face_size == 512

    def test_init_custom_params(self, model_checkpoint):
        """Test initialization with custom parameters."""
        model = GFPGANModel(
            device="cpu",
            model_path=model_checkpoint,
            upscale_factor=4,
            bg_upsampler="realesrgan",
            face_size=1024,
        )
        assert model.device == "cpu"
        assert model.model_path == model_checkpoint
        assert model.upscale_factor == 4
        assert model.bg_upsampler == "realesrgan"
        assert model.face_size == 1024

    def test_init_invalid_device(self):
        """Test initialization with invalid device."""
        with pytest.raises(ValueError, match="Invalid device"):
            GFPGANModel(device="invalid")

    @patch("torch.cuda.is_available", return_value=False)
    def test_init_cuda_not_available(self, mock_cuda):
        """Test initialization with CUDA when not available."""
        with pytest.raises(ValueError, match="CUDA device requested but not available"):
            GFPGANModel(device="cuda")

    def test_init_invalid_upscale_factor(self):
        """Test initialization with invalid upscale factor."""
        with pytest.raises(ValueError, match="Invalid upscale_factor"):
            GFPGANModel(upscale_factor=5)

    def test_init_model_path_not_found(self):
        """Test initialization with non-existent model path."""
        with pytest.raises(FileNotFoundError, match="Model checkpoint not found"):
            GFPGANModel(model_path="/nonexistent/path.pth")

    def test_init_invalid_bg_upsampler(self):
        """Test initialization with invalid background upsampler."""
        with pytest.raises(ValueError, match="Invalid bg_upsampler"):
            GFPGANModel(bg_upsampler="invalid")


class TestGFPGANModelFaceDetection:
    """Tests for face detection functionality."""

    def test_detect_faces_valid_image(self):
        """Test face detection with valid image."""
        model = GFPGANModel()
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        faces = model.detect_faces(image)

        assert isinstance(faces, list)
        assert len(faces) > 0
        assert all(len(face) == 4 for face in faces)

    def test_detect_faces_invalid_input(self):
        """Test face detection with invalid input."""
        model = GFPGANModel()

        with pytest.raises(ValueError, match="Image must be a numpy array"):
            model.detect_faces("not_an_array")

    def test_detect_faces_invalid_shape(self):
        """Test face detection with invalid image shape."""
        model = GFPGANModel()
        image = np.random.randint(0, 255, (480, 640), dtype=np.uint8)

        with pytest.raises(ValueError, match="Image must be RGB with shape"):
            model.detect_faces(image)


class TestGFPGANModelEnhancement:
    """Tests for face enhancement functionality."""

    def test_enhance_face_valid_image(self, sample_image, model_checkpoint, temp_dir):
        """Test face enhancement with valid image."""
        model = GFPGANModel(model_path=model_checkpoint)
        output_path = os.path.join(temp_dir, "enhanced.png")

        result_path = model.enhance_face(sample_image, output_path)

        assert result_path == output_path
        assert os.path.exists(result_path)

    def test_enhance_face_auto_output_path(self, sample_image, model_checkpoint):
        """Test face enhancement with automatic output path."""
        model = GFPGANModel(model_path=model_checkpoint)

        result_path = model.enhance_face(sample_image)

        assert os.path.exists(result_path)
        assert result_path.endswith(".png")

    def test_enhance_face_image_not_found(self):
        """Test face enhancement with non-existent image."""
        model = GFPGANModel()

        with pytest.raises(FileNotFoundError, match="Image file not found"):
            model.enhance_face("/nonexistent/image.jpg")

    def test_enhance_face_invalid_image(self, temp_dir):
        """Test face enhancement with invalid image file."""
        invalid_path = os.path.join(temp_dir, "invalid.jpg")
        Path(invalid_path).write_text("not an image")

        model = GFPGANModel()

        with pytest.raises(ValueError, match="Failed to load image"):
            model.enhance_face(invalid_path)

    def test_enhance_face_with_model_path(self, sample_image, model_checkpoint, temp_dir):
        """Test face enhancement with model checkpoint."""
        model = GFPGANModel(model_path=model_checkpoint)
        output_path = os.path.join(temp_dir, "enhanced.png")

        result_path = model.enhance_face(sample_image, output_path)

        assert os.path.exists(result_path)

    def test_enhance_face_no_model_path(self, sample_image):
        """Test face enhancement without model path."""
        model = GFPGANModel()

        with pytest.raises(ValueError, match="Model path not provided"):
            model.enhance_face(sample_image)

    @patch.object(GFPGANModel, "detect_faces", return_value=[])
    def test_enhance_face_no_faces_detected(self, mock_detect, sample_image):
        """Test face enhancement when no faces are detected."""
        model = GFPGANModel()

        with pytest.raises(ValueError, match="No faces detected in image"):
            model.enhance_face(sample_image)


class TestGFPGANModelVideoEnhancement:
    """Tests for video enhancement functionality."""

    def test_enhance_video_valid_video(self, sample_video, model_checkpoint, temp_dir):
        """Test video enhancement with valid video."""
        model = GFPGANModel(model_path=model_checkpoint)
        output_path = os.path.join(temp_dir, "enhanced.mp4")

        result_path = model.enhance_video(sample_video, output_path)

        assert result_path == output_path
        assert os.path.exists(result_path)

    def test_enhance_video_auto_output_path(self, sample_video, model_checkpoint):
        """Test video enhancement with automatic output path."""
        model = GFPGANModel(model_path=model_checkpoint)

        result_path = model.enhance_video(sample_video)

        assert os.path.exists(result_path)
        assert result_path.endswith(".mp4")

    def test_enhance_video_custom_fps(self, sample_video, model_checkpoint, temp_dir):
        """Test video enhancement with custom FPS."""
        model = GFPGANModel(model_path=model_checkpoint)
        output_path = os.path.join(temp_dir, "enhanced.mp4")

        result_path = model.enhance_video(sample_video, output_path, fps=30)

        assert os.path.exists(result_path)

    def test_enhance_video_not_found(self):
        """Test video enhancement with non-existent video."""
        model = GFPGANModel()

        with pytest.raises(FileNotFoundError, match="Video file not found"):
            model.enhance_video("/nonexistent/video.mp4")

    def test_enhance_video_with_frames_without_faces(self, temp_dir, model_checkpoint):
        """Test video enhancement with frames that have no faces."""
        video_path = os.path.join(temp_dir, "test_video.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(video_path, fourcc, 25, (640, 480))

        for _ in range(5):
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            out.write(frame)

        out.release()

        model = GFPGANModel(model_path=model_checkpoint)

        with patch.object(model, "detect_faces", return_value=[]):
            output_path = os.path.join(temp_dir, "enhanced.mp4")
            result_path = model.enhance_video(video_path, output_path)

            assert os.path.exists(result_path)

    def test_extract_video_frames_empty_video(self, temp_dir):
        """Test extracting frames from an empty video."""
        video_path = os.path.join(temp_dir, "empty_video.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(video_path, fourcc, 25, (640, 480))
        out.release()

        model = GFPGANModel()

        with pytest.raises(ValueError, match="No frames extracted from video"):
            model._extract_video_frames(video_path)

    def test_save_video_no_frames(self, temp_dir):
        """Test saving video with no frames."""
        model = GFPGANModel()
        output_path = os.path.join(temp_dir, "output.mp4")

        with pytest.raises(ValueError, match="No frames to save"):
            model._save_video([], output_path, 25)


class TestGFPGANModelCleanup:
    """Tests for resource cleanup."""

    def test_cleanup(self):
        """Test resource cleanup."""
        model = GFPGANModel()
        model._model = "mock_model"
        model._face_detector = "mock_detector"

        model.cleanup()

        assert model._model is None
        assert model._face_detector is None

    @patch("torch.cuda.is_available", return_value=True)
    @patch("torch.cuda.empty_cache")
    def test_cleanup_with_cuda(self, mock_empty_cache, mock_cuda_available):
        """Test cleanup with CUDA cache clearing."""
        model = GFPGANModel()

        model.cleanup()

        mock_empty_cache.assert_called_once()

