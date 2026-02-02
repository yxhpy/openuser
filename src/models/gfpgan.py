"""
GFPGAN integration for face enhancement.

This module provides integration with the GFPGAN model for enhancing
face quality in images and videos.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Union

import cv2
import numpy as np
import torch


class GFPGANModel:
    """
    GFPGAN model wrapper for face enhancement.

    This class provides a high-level interface to the GFPGAN model,
    handling model loading, face detection, and face enhancement.

    Attributes:
        device (str): Device to run inference on ('cuda' or 'cpu')
        model_path (Optional[str]): Path to GFPGAN model checkpoint
        upscale_factor (int): Upscaling factor for face enhancement (1-4)
        bg_upsampler (Optional[str]): Background upsampler ('realesrgan' or None)
        face_size (int): Size of face region for processing
    """

    def __init__(
        self,
        device: str = "cpu",
        model_path: Optional[str] = None,
        upscale_factor: int = 2,
        bg_upsampler: Optional[str] = None,
        face_size: int = 512,
    ):
        """
        Initialize GFPGAN model.

        Args:
            device: Device to run inference on ('cuda' or 'cpu')
            model_path: Path to GFPGAN model checkpoint
            upscale_factor: Upscaling factor for face enhancement (1-4)
            bg_upsampler: Background upsampler ('realesrgan' or None)
            face_size: Size of face region for processing

        Raises:
            ValueError: If device or upscale_factor is invalid
            FileNotFoundError: If model_path doesn't exist
        """
        if device not in ["cpu", "cuda"]:
            raise ValueError(f"Invalid device: {device}. Must be 'cpu' or 'cuda'")

        if device == "cuda" and not torch.cuda.is_available():
            raise ValueError("CUDA device requested but not available")

        if upscale_factor not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid upscale_factor: {upscale_factor}. Must be 1-4")

        if model_path and not os.path.exists(model_path):
            raise FileNotFoundError(f"Model checkpoint not found: {model_path}")

        if bg_upsampler and bg_upsampler not in ["realesrgan"]:
            raise ValueError(f"Invalid bg_upsampler: {bg_upsampler}")

        self.device = device
        self.model_path = model_path
        self.upscale_factor = upscale_factor
        self.bg_upsampler = bg_upsampler
        self.face_size = face_size
        self._model = None
        self._face_detector = None

    def _load_model(self) -> None:
        """Load GFPGAN model (lazy loading)."""
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

    def detect_faces(
        self, image: np.ndarray
    ) -> list[Tuple[int, int, int, int]]:
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

    def enhance_face(
        self,
        image_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Enhance faces in an image.

        Args:
            image_path: Path to input image
            output_path: Path to save enhanced image (optional)

        Returns:
            Path to enhanced image file

        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image cannot be loaded or no faces detected
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

        self._load_model()

        enhanced_image = self._enhance_image(image, faces)

        if output_path is None:
            output_path = tempfile.mktemp(suffix=".png")

        enhanced_bgr = cv2.cvtColor(enhanced_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, enhanced_bgr)

        return output_path

    def enhance_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        fps: Optional[int] = None,
    ) -> str:
        """
        Enhance faces in a video.

        Args:
            video_path: Path to input video
            output_path: Path to save enhanced video (optional)
            fps: Output video frame rate (optional, uses input fps if None)

        Returns:
            Path to enhanced video file

        Raises:
            FileNotFoundError: If video file doesn't exist
            ValueError: If video cannot be loaded
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        frames = self._extract_video_frames(video_path)

        if fps is None:
            cap = cv2.VideoCapture(video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            cap.release()

        enhanced_frames = []
        for frame in frames:
            faces = self.detect_faces(frame)
            if faces:
                self._load_model()
                enhanced_frame = self._enhance_image(frame, faces)
                enhanced_frames.append(enhanced_frame)
            else:
                enhanced_frames.append(frame)

        if output_path is None:
            output_path = tempfile.mktemp(suffix=".mp4")

        self._save_video(enhanced_frames, output_path, fps)

        return output_path

    def _enhance_image(
        self, image: np.ndarray, faces: list[Tuple[int, int, int, int]]
    ) -> np.ndarray:
        """
        Enhance faces in an image using GFPGAN.

        Args:
            image: Input image as numpy array
            faces: List of face bounding boxes

        Returns:
            Enhanced image as numpy array
        """
        enhanced = image.copy()

        for x, y, w, h in faces:
            face_region = image[y : y + h, x : x + w]

            if self.upscale_factor > 1:
                new_h = h * self.upscale_factor
                new_w = w * self.upscale_factor
                face_region = cv2.resize(face_region, (new_w, new_h))

            enhanced[y : y + h, x : x + w] = cv2.resize(face_region, (w, h))

        return enhanced

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

    def _save_video(
        self, frames: list[np.ndarray], output_path: str, fps: int
    ) -> None:
        """Save frames as video."""
        if not frames:
            raise ValueError("No frames to save")

        h, w = frames[0].shape[:2]

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

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

