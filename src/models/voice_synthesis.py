"""
Voice synthesis module for text-to-speech generation.

This module provides TTS (Text-to-Speech) functionality with support for multiple backends:
- Coqui TTS: High-quality neural TTS with voice cloning
- pyttsx3: Offline TTS engine
- gTTS: Google Text-to-Speech API

Features:
- Multiple TTS backend support
- Device management (CPU/GPU)
- Model caching
- Voice cloning support
- Audio format conversion
"""

import os
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, Union

import torch


class TTSBackend(str, Enum):
    """Supported TTS backends."""

    COQUI = "coqui"
    PYTTSX3 = "pyttsx3"
    GTTS = "gtts"


class VoiceSynthesizer:
    """
    Voice synthesizer with multiple TTS backend support.

    Attributes:
        backend: TTS backend to use
        device: Device for model inference (cpu/cuda)
        model_path: Path to TTS model (for Coqui TTS)
        sample_rate: Audio sample rate
    """

    def __init__(
        self,
        backend: TTSBackend = TTSBackend.COQUI,
        device: str = "cpu",
        model_path: Optional[str] = None,
        sample_rate: int = 22050,
    ) -> None:
        """
        Initialize voice synthesizer.

        Args:
            backend: TTS backend to use
            device: Device for model inference (cpu/cuda)
            model_path: Path to TTS model (for Coqui TTS)
            sample_rate: Audio sample rate

        Raises:
            ValueError: If backend is not supported
            RuntimeError: If model initialization fails
        """
        self.backend = backend
        self.device = device if torch.cuda.is_available() else "cpu"
        self.model_path = model_path
        self.sample_rate = sample_rate
        self._model: Optional[object] = None
        self._engine: Optional[object] = None

        self._initialize_backend()

    def _initialize_backend(self) -> None:
        """Initialize the selected TTS backend."""
        if self.backend == TTSBackend.COQUI:
            self._initialize_coqui()
        elif self.backend == TTSBackend.PYTTSX3:
            self._initialize_pyttsx3()
        elif self.backend == TTSBackend.GTTS:
            # gTTS doesn't require initialization
            pass
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def _initialize_coqui(self) -> None:
        """Initialize Coqui TTS backend."""
        try:
            from TTS.api import TTS

            if self.model_path:
                self._model = TTS(model_path=self.model_path, gpu=(self.device == "cuda"))
            else:
                # Use default model
                self._model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", gpu=(self.device == "cuda"))
        except ImportError as e:
            raise RuntimeError(f"Failed to import Coqui TTS: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Coqui TTS: {e}")

    def _initialize_pyttsx3(self) -> None:
        """Initialize pyttsx3 TTS backend."""
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 150)
            self._engine.setProperty("volume", 1.0)
        except ImportError as e:
            raise RuntimeError(f"Failed to import pyttsx3: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize pyttsx3: {e}")

    def synthesize(
        self, text: str, output_path: Optional[str] = None, speaker_wav: Optional[str] = None
    ) -> str:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            output_path: Path to save audio file (if None, creates temp file)
            speaker_wav: Path to speaker audio for voice cloning (Coqui only)

        Returns:
            Path to generated audio file

        Raises:
            ValueError: If text is empty
            RuntimeError: If synthesis fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav")

        if self.backend == TTSBackend.COQUI:
            return self._synthesize_coqui(text, output_path, speaker_wav)
        elif self.backend == TTSBackend.PYTTSX3:
            return self._synthesize_pyttsx3(text, output_path)
        elif self.backend == TTSBackend.GTTS:
            return self._synthesize_gtts(text, output_path)
        else:
            raise RuntimeError(f"Backend {self.backend} not initialized")

    def _synthesize_coqui(
        self, text: str, output_path: str, speaker_wav: Optional[str] = None
    ) -> str:
        """Synthesize speech using Coqui TTS."""
        try:
            if speaker_wav and hasattr(self._model, "tts_to_file"):
                # Voice cloning
                self._model.tts_to_file(
                    text=text, file_path=output_path, speaker_wav=speaker_wav
                )
            else:
                # Standard TTS
                self._model.tts_to_file(text=text, file_path=output_path)
            return output_path
        except Exception as e:
            raise RuntimeError(f"Coqui TTS synthesis failed: {e}")

    def _synthesize_pyttsx3(self, text: str, output_path: str) -> str:
        """Synthesize speech using pyttsx3."""
        try:
            if self._engine is None:
                raise RuntimeError("pyttsx3 engine not initialized")
            self._engine.save_to_file(text, output_path)
            self._engine.runAndWait()
            return output_path
        except Exception as e:
            raise RuntimeError(f"pyttsx3 synthesis failed: {e}")

    def _synthesize_gtts(self, text: str, output_path: str) -> str:
        """Synthesize speech using gTTS."""
        try:
            from gtts import gTTS

            tts = gTTS(text=text, lang="en")
            tts.save(output_path)
            return output_path
        except ImportError as e:
            raise RuntimeError(f"Failed to import gTTS: {e}")
        except Exception as e:
            raise RuntimeError(f"gTTS synthesis failed: {e}")

    def list_available_models(self) -> list[str]:
        """
        List available TTS models for the current backend.

        Returns:
            List of available model names

        Raises:
            RuntimeError: If backend doesn't support model listing
        """
        if self.backend == TTSBackend.COQUI:
            try:
                from TTS.api import TTS

                return TTS.list_models()
            except Exception as e:
                raise RuntimeError(f"Failed to list Coqui models: {e}")
        elif self.backend == TTSBackend.PYTTSX3:
            # pyttsx3 uses system voices
            if self._engine:
                voices = self._engine.getProperty("voices")
                return [voice.name for voice in voices]
            return []
        elif self.backend == TTSBackend.GTTS:
            # gTTS supports multiple languages
            return ["en", "es", "fr", "de", "it", "pt", "ru", "zh-CN", "ja", "ko"]
        else:
            raise RuntimeError(f"Backend {self.backend} doesn't support model listing")

    def cleanup(self) -> None:
        """Clean up resources."""
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass
        self._model = None
        self._engine = None
