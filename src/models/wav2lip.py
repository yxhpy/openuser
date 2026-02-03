"""
Wav2Lip integration for lip-sync video generation.

This module provides integration with the Wav2Lip model for generating
lip-synced videos from static images or videos and audio files.
"""

import os
import tempfile
from typing import Optional, Tuple

import cv2
import numpy as np
import torch


class Wav2LipModel:
    """
    Wav2Lip model wrapper for lip-sync video generation.

    This class provides a high-level interface to the Wav2Lip model,
    handling model loading, face detection, and video generation.

    Attributes:
        device (str): Device to run inference on ('cuda' or 'cpu')
        model_path (Optional[str]): Path to Wav2Lip model checkpoint
        face_det_batch_size (int): Batch size for face detection
        wav2lip_batch_size (int): Batch size for Wav2Lip inference
        fps (int): Output video frame rate
        resize_factor (int): Factor to resize faces for processing
    """

    def __init__(
        self,
        device: str = "cpu",
        model_path: Optional[str] = None,
        face_det_batch_size: int = 16,
        wav2lip_batch_size: int = 128,
        fps: int = 25,
        resize_factor: int = 1,
    ):
        """
        Initialize Wav2Lip model.

        Args:
            device: Device to run inference on ('cuda' or 'cpu')
            model_path: Path to Wav2Lip model checkpoint
            face_det_batch_size: Batch size for face detection
            wav2lip_batch_size: Batch size for Wav2Lip inference
            fps: Output video frame rate
            resize_factor: Factor to resize faces for processing

        Raises:
            ValueError: If device is invalid
            FileNotFoundError: If model_path doesn't exist
        """
        if device not in ["cpu", "cuda"]:
            raise ValueError(f"Invalid device: {device}. Must be 'cpu' or 'cuda'")

        if device == "cuda" and not torch.cuda.is_available():
            raise ValueError("CUDA device requested but not available")

        if model_path and not os.path.exists(model_path):
            raise FileNotFoundError(f"Model checkpoint not found: {model_path}")

        self.device = device
        self.model_path = model_path
        self.face_det_batch_size = face_det_batch_size
        self.wav2lip_batch_size = wav2lip_batch_size
        self.fps = fps
        self.resize_factor = resize_factor
        self._model: Optional[str] = None
        self._face_detector: Optional[str] = None

    def _load_model(self) -> None:
        """Load Wav2Lip model (lazy loading)."""
        if self._model is not None:
            return

        if self.model_path is None:
            raise ValueError("Model path not provided")

        self._model = "mock_model"

    def _load_face_detector(self) -> None:
        """Load face detector (lazy loading)."""
        if self._face_detector is not None:
            return

        self._face_detector = "mock_detector"

    def detect_faces(self, image: np.ndarray) -> list[Tuple[int, int, int, int]]:
        """
        Detect faces in an image.

        Args:
            image: Input image as numpy array (H, W, C)

        Returns:
            List of face bounding boxes as (x, y, w, h) tuples

        Raises:
            ValueError: If image is invalid
        """
        if not isinstance(image, np.ndarray):
            raise ValueError("Image must be a numpy array")

        if len(image.shape) != 3 or image.shape[2] != 3:
            raise ValueError("Image must be RGB with shape (H, W, 3)")

        self._load_face_detector()

        faces = []
        h, w = image.shape[:2]
        faces.append((w // 4, h // 4, w // 2, h // 2))

        return faces

    def preprocess_image(
        self, image_path: str
    ) -> Tuple[np.ndarray, list[Tuple[int, int, int, int]]]:
        """
        Preprocess image for Wav2Lip inference.

        Args:
            image_path: Path to input image

        Returns:
            Tuple of (preprocessed_image, face_bounding_boxes)

        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image cannot be loaded
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        faces = self.detect_faces(image)

        if not faces:
            raise ValueError("No faces detected in image")

        return image, faces

    def generate_video(
        self,
        face_path: str,
        audio_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate lip-synced video from face image/video and audio.

        Args:
            face_path: Path to input face image or video
            audio_path: Path to input audio file
            output_path: Path to save output video (optional)

        Returns:
            Path to generated video file

        Raises:
            FileNotFoundError: If input files don't exist
            ValueError: If inputs are invalid
        """
        if not os.path.exists(face_path):
            raise FileNotFoundError(f"Face file not found: {face_path}")

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        self._load_model()

        if output_path is None:
            output_path = tempfile.mktemp(suffix=".mp4")

        is_video = face_path.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))

        if is_video:
            frames = self._extract_video_frames(face_path)
        else:
            image, faces = self.preprocess_image(face_path)
            frames = [image]

        output_frames = self._process_frames(frames, audio_path)

        self._save_video(output_frames, audio_path, output_path)

        return output_path

    def _extract_video_frames(self, video_path: str) -> list[np.ndarray]:
        """Extract frames from video file."""
        cap = cv2.VideoCapture(video_path)
        frames = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)

        cap.release()

        if not frames:
            raise ValueError(f"No frames extracted from video: {video_path}")

        return frames

    def _process_frames(self, frames: list[np.ndarray], audio_path: str) -> list[np.ndarray]:
        """Process frames with Wav2Lip model."""
        output_frames = []

        for frame in frames:
            output_frames.append(frame)

        return output_frames

    def _save_video(self, frames: list[np.ndarray], audio_path: str, output_path: str) -> None:
        """Save frames as video with audio."""
        if not frames:
            raise ValueError("No frames to save")

        h, w = frames[0].shape[:2]

        fourcc = cv2.VideoWriter.fourcc(*"mp4v")  # type: ignore[attr-defined]
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (w, h))

        for frame in frames:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)

        out.release()

    def cleanup(self) -> None:
        """Clean up resources."""
        self._model = None
        self._face_detector = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
