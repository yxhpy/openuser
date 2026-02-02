"""
Tests for Wav2Lip integration module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest
import torch

from src.models.wav2lip import Wav2LipModel


class TestWav2LipModel:
    """Test cases for Wav2LipModel class."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        model = Wav2LipModel()

        assert model.device == "cpu"
        assert model.model_path is None
        assert model.face_det_batch_size == 16
        assert model.wav2lip_batch_size == 128
        assert model.fps == 25
        assert model.resize_factor == 1
        assert model._model is None
        assert model._face_detector is None

    def test_init_custom(self, tmp_path):
        """Test initialization with custom parameters."""
        model_path = tmp_path / "model.pth"
        model_path.touch()

        model = Wav2LipModel(
            device="cpu",
            model_path=str(model_path),
            face_det_batch_size=8,
            wav2lip_batch_size=64,
            fps=30,
            resize_factor=2,
        )

        assert model.device == "cpu"
        assert model.model_path == str(model_path)
        assert model.face_det_batch_size == 8
        assert model.wav2lip_batch_size == 64
        assert model.fps == 30
        assert model.resize_factor == 2

    def test_init_invalid_device(self):
        """Test initialization with invalid device."""
        with pytest.raises(ValueError, match="Invalid device"):
            Wav2LipModel(device="invalid")

    @patch("torch.cuda.is_available", return_value=False)
    def test_init_cuda_not_available(self, mock_cuda):
        """Test initialization with CUDA when not available."""
        with pytest.raises(ValueError, match="CUDA device requested"):
            Wav2LipModel(device="cuda")

    def test_init_model_path_not_exists(self):
        """Test initialization with non-existent model path."""
        with pytest.raises(FileNotFoundError, match="Model checkpoint not found"):
            Wav2LipModel(model_path="/nonexistent/model.pth")

    def test_load_model(self, tmp_path):
        """Test lazy model loading."""
        model_path = tmp_path / "model.pth"
        model_path.touch()

        model = Wav2LipModel(model_path=str(model_path))
        assert model._model is None

        model._load_model()
        assert model._model is not None

        model._load_model()
        assert model._model is not None

    def test_load_model_no_path(self):
        """Test model loading without path."""
        model = Wav2LipModel()

        with pytest.raises(ValueError, match="Model path not provided"):
            model._load_model()

    def test_load_face_detector(self):
        """Test lazy face detector loading."""
        model = Wav2LipModel()
        assert model._face_detector is None

        model._load_face_detector()
        assert model._face_detector is not None

        model._load_face_detector()
        assert model._face_detector is not None

    def test_detect_faces_valid_image(self):
        """Test face detection with valid image."""
        model = Wav2LipModel()
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        faces = model.detect_faces(image)

        assert isinstance(faces, list)
        assert len(faces) > 0
        assert all(len(face) == 4 for face in faces)

    def test_detect_faces_invalid_type(self):
        """Test face detection with invalid input type."""
        model = Wav2LipModel()

        with pytest.raises(ValueError, match="Image must be a numpy array"):
            model.detect_faces("not_an_array")

    def test_detect_faces_invalid_shape(self):
        """Test face detection with invalid image shape."""
        model = Wav2LipModel()
        image = np.random.randint(0, 255, (480, 640), dtype=np.uint8)

        with pytest.raises(ValueError, match="Image must be RGB"):
            model.detect_faces(image)

    def test_preprocess_image_valid(self, tmp_path):
        """Test image preprocessing with valid image."""
        image_path = tmp_path / "test.jpg"
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite(str(image_path), test_image)

        model = Wav2LipModel()
        image, faces = model.preprocess_image(str(image_path))

        assert isinstance(image, np.ndarray)
        assert image.shape[2] == 3
        assert isinstance(faces, list)
        assert len(faces) > 0

    def test_preprocess_image_not_found(self):
        """Test image preprocessing with non-existent file."""
        model = Wav2LipModel()

        with pytest.raises(FileNotFoundError, match="Image file not found"):
            model.preprocess_image("/nonexistent/image.jpg")

    def test_preprocess_image_invalid(self, tmp_path):
        """Test image preprocessing with invalid image file."""
        image_path = tmp_path / "invalid.jpg"
        image_path.write_text("not an image")

        model = Wav2LipModel()

        with pytest.raises(ValueError, match="Failed to load image"):
            model.preprocess_image(str(image_path))

    def test_preprocess_image_no_faces(self, tmp_path):
        """Test image preprocessing when no faces detected."""
        image_path = tmp_path / "test.jpg"
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite(str(image_path), test_image)

        model = Wav2LipModel()

        with patch.object(model, 'detect_faces', return_value=[]):
            with pytest.raises(ValueError, match="No faces detected"):
                model.preprocess_image(str(image_path))

    def test_generate_video_with_image(self, tmp_path):
        """Test video generation from image and audio."""
        image_path = tmp_path / "face.jpg"
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite(str(image_path), test_image)

        audio_path = tmp_path / "audio.wav"
        audio_path.touch()

        model_path = tmp_path / "model.pth"
        model_path.touch()

        output_path = tmp_path / "output.mp4"

        model = Wav2LipModel(model_path=str(model_path))
        result = model.generate_video(
            str(image_path), str(audio_path), str(output_path)
        )

        assert result == str(output_path)
        assert os.path.exists(result)

    def test_generate_video_with_video(self, tmp_path):
        """Test video generation from video and audio."""
        video_path = tmp_path / "face.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(video_path), fourcc, 25, (640, 480))
        for _ in range(10):
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

        audio_path = tmp_path / "audio.wav"
        audio_path.touch()

        model_path = tmp_path / "model.pth"
        model_path.touch()

        output_path = tmp_path / "output.mp4"

        model = Wav2LipModel(model_path=str(model_path))
        result = model.generate_video(
            str(video_path), str(audio_path), str(output_path)
        )

        assert result == str(output_path)
        assert os.path.exists(result)

    def test_generate_video_auto_output_path(self, tmp_path):
        """Test video generation with automatic output path."""
        image_path = tmp_path / "face.jpg"
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite(str(image_path), test_image)

        audio_path = tmp_path / "audio.wav"
        audio_path.touch()

        model_path = tmp_path / "model.pth"
        model_path.touch()

        model = Wav2LipModel(model_path=str(model_path))
        result = model.generate_video(str(image_path), str(audio_path))

        assert result.endswith(".mp4")
        assert os.path.exists(result)

        os.remove(result)

    def test_generate_video_face_not_found(self, tmp_path):
        """Test video generation with non-existent face file."""
        audio_path = tmp_path / "audio.wav"
        audio_path.touch()

        model_path = tmp_path / "model.pth"
        model_path.touch()

        model = Wav2LipModel(model_path=str(model_path))

        with pytest.raises(FileNotFoundError, match="Face file not found"):
            model.generate_video("/nonexistent/face.jpg", str(audio_path))

    def test_generate_video_audio_not_found(self, tmp_path):
        """Test video generation with non-existent audio file."""
        image_path = tmp_path / "face.jpg"
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite(str(image_path), test_image)

        model_path = tmp_path / "model.pth"
        model_path.touch()

        model = Wav2LipModel(model_path=str(model_path))

        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            model.generate_video(str(image_path), "/nonexistent/audio.wav")

    def test_extract_video_frames(self, tmp_path):
        """Test video frame extraction."""
        video_path = tmp_path / "test.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(video_path), fourcc, 25, (640, 480))
        for _ in range(5):
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

        model = Wav2LipModel()
        frames = model._extract_video_frames(str(video_path))

        assert isinstance(frames, list)
        assert len(frames) == 5
        assert all(isinstance(f, np.ndarray) for f in frames)

    def test_extract_video_frames_empty(self, tmp_path):
        """Test video frame extraction with empty video."""
        video_path = tmp_path / "empty.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(video_path), fourcc, 25, (640, 480))
        out.release()

        model = Wav2LipModel()

        with pytest.raises(ValueError, match="No frames extracted"):
            model._extract_video_frames(str(video_path))

    def test_process_frames(self, tmp_path):
        """Test frame processing."""
        frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(3)
        ]

        audio_path = tmp_path / "audio.wav"
        audio_path.touch()

        model = Wav2LipModel()
        output_frames = model._process_frames(frames, str(audio_path))

        assert isinstance(output_frames, list)
        assert len(output_frames) == len(frames)

    def test_save_video(self, tmp_path):
        """Test video saving."""
        frames = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            for _ in range(5)
        ]

        audio_path = tmp_path / "audio.wav"
        audio_path.touch()

        output_path = tmp_path / "output.mp4"

        model = Wav2LipModel()
        model._save_video(frames, str(audio_path), str(output_path))

        assert os.path.exists(output_path)

        cap = cv2.VideoCapture(str(output_path))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        assert frame_count == len(frames)

    def test_save_video_empty_frames(self, tmp_path):
        """Test video saving with empty frames."""
        audio_path = tmp_path / "audio.wav"
        audio_path.touch()

        output_path = tmp_path / "output.mp4"

        model = Wav2LipModel()

        with pytest.raises(ValueError, match="No frames to save"):
            model._save_video([], str(audio_path), str(output_path))

    def test_cleanup(self):
        """Test resource cleanup."""
        model = Wav2LipModel()
        model._model = "mock_model"
        model._face_detector = "mock_detector"

        model.cleanup()

        assert model._model is None
        assert model._face_detector is None

    @patch("torch.cuda.is_available", return_value=True)
    @patch("torch.cuda.empty_cache")
    def test_cleanup_with_cuda(self, mock_empty_cache, mock_cuda):
        """Test resource cleanup with CUDA."""
        model = Wav2LipModel()
        model._model = "mock_model"

        model.cleanup()

        mock_empty_cache.assert_called_once()




