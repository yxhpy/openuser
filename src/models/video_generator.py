"""
Video generation pipeline for digital human.

This module provides a unified pipeline that integrates voice synthesis,
lip-sync, face enhancement, and talking head generation.
"""

import os
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np

from src.models.voice_synthesis import VoiceSynthesizer
from src.models.wav2lip import Wav2LipModel
from src.models.gfpgan import GFPGANModel
from src.models.sadtalker import SadTalkerModel


class GenerationMode(Enum):
    """Video generation modes."""

    LIPSYNC = "lipsync"  # Wav2Lip only
    TALKING_HEAD = "talking_head"  # SadTalker
    ENHANCED_LIPSYNC = "enhanced_lipsync"  # Wav2Lip + GFPGAN
    ENHANCED_TALKING_HEAD = "enhanced_talking_head"  # SadTalker + GFPGAN


class VideoGenerator:
    """
    Unified video generation pipeline for digital human.

    This class orchestrates the full pipeline from text/audio to final video,
    integrating voice synthesis, lip-sync, face enhancement, and talking head generation.

    Attributes:
        device (str): Device to run inference on ('cuda' or 'cpu')
        mode (GenerationMode): Video generation mode
        voice_synthesizer (Optional[VoiceSynthesizer]): Voice synthesis component
        wav2lip_model (Optional[Wav2LipModel]): Wav2Lip component
        gfpgan_model (Optional[GFPGANModel]): GFPGAN component
        sadtalker_model (Optional[SadTalkerModel]): SadTalker component
    """

    def __init__(
        self,
        device: str = "cpu",
        mode: GenerationMode = GenerationMode.LIPSYNC,
        voice_config: Optional[Dict[str, Any]] = None,
        wav2lip_config: Optional[Dict[str, Any]] = None,
        gfpgan_config: Optional[Dict[str, Any]] = None,
        sadtalker_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize video generation pipeline.

        Args:
            device: Device to run inference on ('cuda' or 'cpu')
            mode: Video generation mode
            voice_config: Configuration for voice synthesizer
            wav2lip_config: Configuration for Wav2Lip model
            gfpgan_config: Configuration for GFPGAN model
            sadtalker_config: Configuration for SadTalker model

        Raises:
            ValueError: If mode is invalid or required components are missing
        """
        if not isinstance(mode, GenerationMode):
            raise ValueError(f"Invalid mode: {mode}. Must be a GenerationMode enum")

        self.device = device
        self.mode = mode

        voice_config = voice_config or {}
        wav2lip_config = wav2lip_config or {}
        gfpgan_config = gfpgan_config or {}
        sadtalker_config = sadtalker_config or {}

        self.voice_synthesizer = None
        self.wav2lip_model = None
        self.gfpgan_model = None
        self.sadtalker_model = None

        if mode in [GenerationMode.LIPSYNC, GenerationMode.ENHANCED_LIPSYNC]:
            self.wav2lip_model = Wav2LipModel(device=device, **wav2lip_config)

        if mode in [GenerationMode.TALKING_HEAD, GenerationMode.ENHANCED_TALKING_HEAD]:
            self.sadtalker_model = SadTalkerModel(device=device, **sadtalker_config)

        if mode in [GenerationMode.ENHANCED_LIPSYNC, GenerationMode.ENHANCED_TALKING_HEAD]:
            self.gfpgan_model = GFPGANModel(device=device, **gfpgan_config)

    def generate_from_text(
        self,
        text: str,
        image_path: str,
        output_path: Optional[str] = None,
        speaker_wav: Optional[str] = None,
    ) -> str:
        """
        Generate video from text and image.

        Args:
            text: Input text to synthesize
            image_path: Path to face image
            output_path: Path to save output video (optional)
            speaker_wav: Path to speaker reference audio for voice cloning (optional)

        Returns:
            Path to generated video file

        Raises:
            ValueError: If voice synthesizer is not initialized
            FileNotFoundError: If image file doesn't exist
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        if self.voice_synthesizer is None:
            raise ValueError("Voice synthesizer not initialized")

        audio_path = self.voice_synthesizer.synthesize(
            text=text, speaker_wav=speaker_wav
        )

        try:
            return self.generate_from_audio(image_path, audio_path, output_path)
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

    def generate_from_audio(
        self,
        image_path: str,
        audio_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate video from audio and image.

        Args:
            image_path: Path to face image
            audio_path: Path to audio file
            output_path: Path to save output video (optional)

        Returns:
            Path to generated video file

        Raises:
            FileNotFoundError: If input files don't exist
            ValueError: If required models are not initialized
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if output_path is None:
            output_path = tempfile.mktemp(suffix=".mp4")

        if self.mode == GenerationMode.LIPSYNC:
            return self._generate_lipsync(image_path, audio_path, output_path)
        elif self.mode == GenerationMode.TALKING_HEAD:
            return self._generate_talking_head(image_path, audio_path, output_path)
        elif self.mode == GenerationMode.ENHANCED_LIPSYNC:
            return self._generate_enhanced_lipsync(image_path, audio_path, output_path)
        elif self.mode == GenerationMode.ENHANCED_TALKING_HEAD:
            return self._generate_enhanced_talking_head(image_path, audio_path, output_path)
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

    def _generate_lipsync(
        self, image_path: str, audio_path: str, output_path: str
    ) -> str:
        """Generate lip-sync video using Wav2Lip."""
        if self.wav2lip_model is None:
            raise ValueError("Wav2Lip model not initialized")

        return self.wav2lip_model.generate_video(image_path, audio_path, output_path)

    def _generate_talking_head(
        self, image_path: str, audio_path: str, output_path: str
    ) -> str:
        """Generate talking head video using SadTalker."""
        if self.sadtalker_model is None:
            raise ValueError("SadTalker model not initialized")

        return self.sadtalker_model.generate_video(image_path, audio_path, output_path)

    def _generate_enhanced_lipsync(
        self, image_path: str, audio_path: str, output_path: str
    ) -> str:
        """Generate enhanced lip-sync video using Wav2Lip + GFPGAN."""
        if self.wav2lip_model is None:
            raise ValueError("Wav2Lip model not initialized")
        if self.gfpgan_model is None:
            raise ValueError("GFPGAN model not initialized")

        temp_video = tempfile.mktemp(suffix=".mp4")
        try:
            self.wav2lip_model.generate_video(image_path, audio_path, temp_video)
            return self.gfpgan_model.enhance_video(temp_video, output_path)
        finally:
            if os.path.exists(temp_video):
                os.remove(temp_video)

    def _generate_enhanced_talking_head(
        self, image_path: str, audio_path: str, output_path: str
    ) -> str:
        """Generate enhanced talking head video using SadTalker + GFPGAN."""
        if self.sadtalker_model is None:
            raise ValueError("SadTalker model not initialized")
        if self.gfpgan_model is None:
            raise ValueError("GFPGAN model not initialized")

        temp_video = tempfile.mktemp(suffix=".mp4")
        try:
            self.sadtalker_model.generate_video(image_path, audio_path, temp_video)
            return self.gfpgan_model.enhance_video(temp_video, output_path)
        finally:
            if os.path.exists(temp_video):
                os.remove(temp_video)

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.voice_synthesizer:
            self.voice_synthesizer.cleanup()
        if self.wav2lip_model:
            self.wav2lip_model.cleanup()
        if self.gfpgan_model:
            self.gfpgan_model.cleanup()
        if self.sadtalker_model:
            self.sadtalker_model.cleanup()

