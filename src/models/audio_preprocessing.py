"""
Audio preprocessing and enhancement module.

This module provides audio processing capabilities including:
- Audio format conversion
- Sample rate conversion
- Audio normalization
- Noise reduction
- Silence trimming
- Audio quality validation

Features:
- Multiple audio format support
- Configurable processing parameters
- Batch processing support
- Quality metrics calculation
"""

import os
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import numpy as np
import torch


class AudioFormat(str, Enum):
    """Supported audio formats."""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"


class AudioPreprocessor:
    """
    Audio preprocessing and enhancement system.

    Attributes:
        sample_rate: Target sample rate for audio processing
        device: Device for processing (cpu/cuda)
        normalize: Whether to normalize audio by default
    """

    def __init__(
        self,
        sample_rate: int = 22050,
        device: str = "cpu",
        normalize: bool = True,
    ) -> None:
        """
        Initialize audio preprocessor.

        Args:
            sample_rate: Target sample rate
            device: Device for processing (cpu/cuda)
            normalize: Whether to normalize audio by default
        """
        self.sample_rate = sample_rate
        self.device = device if torch.cuda.is_available() else "cpu"
        self.normalize = normalize

    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of (audio_data, sample_rate)

        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If audio loading fails
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            import librosa

            audio_data, sr = librosa.load(audio_path, sr=None, mono=True)
            return audio_data, sr
        except ImportError as e:
            raise RuntimeError(f"Failed to import librosa: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load audio: {e}")

    def convert_sample_rate(
        self, audio_data: np.ndarray, original_sr: int, target_sr: Optional[int] = None
    ) -> np.ndarray:
        """
        Convert audio sample rate.

        Args:
            audio_data: Audio data array
            original_sr: Original sample rate
            target_sr: Target sample rate (uses self.sample_rate if None)

        Returns:
            Resampled audio data

        Raises:
            RuntimeError: If resampling fails
        """
        if target_sr is None:
            target_sr = self.sample_rate

        if original_sr == target_sr:
            return audio_data

        try:
            import librosa

            return librosa.resample(audio_data, orig_sr=original_sr, target_sr=target_sr)
        except Exception as e:
            raise RuntimeError(f"Failed to resample audio: {e}")

    def normalize_audio(self, audio_data: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """
        Normalize audio to target dB level.

        Args:
            audio_data: Audio data array
            target_db: Target dB level

        Returns:
            Normalized audio data
        """
        # Calculate current RMS
        rms = np.sqrt(np.mean(audio_data**2))

        if rms == 0:
            return audio_data

        # Calculate target RMS from dB
        target_rms = 10 ** (target_db / 20)

        # Normalize
        normalized = audio_data * (target_rms / rms)

        # Clip to prevent overflow
        return np.clip(normalized, -1.0, 1.0)

    def trim_silence(
        self, audio_data: np.ndarray, threshold_db: float = -40.0, frame_length: int = 2048
    ) -> np.ndarray:
        """
        Trim silence from beginning and end of audio.

        Args:
            audio_data: Audio data array
            threshold_db: Silence threshold in dB
            frame_length: Frame length for analysis

        Returns:
            Trimmed audio data

        Raises:
            RuntimeError: If trimming fails
        """
        try:
            import librosa

            trimmed, _ = librosa.effects.trim(
                audio_data, top_db=-threshold_db, frame_length=frame_length
            )
            return trimmed
        except Exception as e:
            raise RuntimeError(f"Failed to trim silence: {e}")

    def reduce_noise(
        self, audio_data: np.ndarray, sr: int, noise_reduce_strength: float = 0.5
    ) -> np.ndarray:
        """
        Reduce noise from audio using spectral gating.

        Args:
            audio_data: Audio data array
            sr: Sample rate
            noise_reduce_strength: Noise reduction strength (0.0 to 1.0)

        Returns:
            Noise-reduced audio data

        Raises:
            RuntimeError: If noise reduction fails
        """
        try:
            import noisereduce as nr

            reduced = nr.reduce_noise(
                y=audio_data, sr=sr, prop_decrease=noise_reduce_strength
            )
            return reduced
        except ImportError:
            # If noisereduce not available, return original audio
            return audio_data
        except Exception as e:
            raise RuntimeError(f"Failed to reduce noise: {e}")

    def save_audio(
        self, audio_data: np.ndarray, output_path: str, sr: Optional[int] = None
    ) -> str:
        """
        Save audio to file.

        Args:
            audio_data: Audio data array
            output_path: Output file path
            sr: Sample rate (uses self.sample_rate if None)

        Returns:
            Path to saved audio file

        Raises:
            RuntimeError: If saving fails
        """
        if sr is None:
            sr = self.sample_rate

        try:
            import soundfile as sf

            sf.write(output_path, audio_data, sr)
            return output_path
        except ImportError as e:
            raise RuntimeError(f"Failed to import soundfile: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to save audio: {e}")

    def convert_format(
        self, input_path: str, output_path: str, target_format: AudioFormat
    ) -> str:
        """
        Convert audio file format.

        Args:
            input_path: Input audio file path
            output_path: Output audio file path
            target_format: Target audio format

        Returns:
            Path to converted audio file

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If conversion fails
        """
        # Load audio
        audio_data, sr = self.load_audio(input_path)

        # Ensure output path has correct extension
        output_path = str(Path(output_path).with_suffix(f".{target_format.value}"))

        # Save in target format
        return self.save_audio(audio_data, output_path, sr)

    def validate_audio_quality(
        self, audio_data: np.ndarray, sr: int
    ) -> Dict[str, Any]:
        """
        Validate audio quality and return metrics.

        Args:
            audio_data: Audio data array
            sr: Sample rate

        Returns:
            Dictionary with quality metrics
        """
        metrics = {
            "duration": len(audio_data) / sr,
            "sample_rate": sr,
            "num_samples": len(audio_data),
            "rms": float(np.sqrt(np.mean(audio_data**2))),
            "peak": float(np.max(np.abs(audio_data))),
            "is_clipped": bool(np.any(np.abs(audio_data) >= 0.99)),
            "is_silent": bool(np.max(np.abs(audio_data)) < 0.01),
        }

        return metrics

    def preprocess(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        target_sr: Optional[int] = None,
        normalize: Optional[bool] = None,
        trim_silence: bool = True,
        reduce_noise: bool = False,
        noise_strength: float = 0.5,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Preprocess audio file with all enhancement steps.

        Args:
            input_path: Input audio file path
            output_path: Output audio file path (creates temp file if None)
            target_sr: Target sample rate (uses self.sample_rate if None)
            normalize: Whether to normalize (uses self.normalize if None)
            trim_silence: Whether to trim silence
            reduce_noise: Whether to reduce noise
            noise_strength: Noise reduction strength (0.0 to 1.0)

        Returns:
            Tuple of (output_path, quality_metrics)

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If preprocessing fails
        """
        # Load audio
        audio_data, original_sr = self.load_audio(input_path)

        # Convert sample rate
        if target_sr is None:
            target_sr = self.sample_rate
        audio_data = self.convert_sample_rate(audio_data, original_sr, target_sr)

        # Trim silence
        if trim_silence:
            audio_data = self.trim_silence(audio_data)

        # Reduce noise
        if reduce_noise:
            audio_data = self.reduce_noise(audio_data, target_sr, noise_strength)

        # Normalize
        if normalize is None:
            normalize = self.normalize
        if normalize:
            audio_data = self.normalize_audio(audio_data)

        # Validate quality
        metrics = self.validate_audio_quality(audio_data, target_sr)

        # Save audio
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav")

        output_path = self.save_audio(audio_data, output_path, target_sr)

        return output_path, metrics

