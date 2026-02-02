"""
Tests for voice synthesis module.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import torch

# Mock TTS, pyttsx3, and gtts modules before importing voice_synthesis
sys.modules["TTS"] = MagicMock()
sys.modules["TTS.api"] = MagicMock()
sys.modules["pyttsx3"] = MagicMock()
sys.modules["gtts"] = MagicMock()

from src.models.voice_synthesis import TTSBackend, VoiceSynthesizer


class TestTTSBackend:
    """Test TTSBackend enum."""

    def test_backend_values(self) -> None:
        """Test backend enum values."""
        assert TTSBackend.COQUI == "coqui"
        assert TTSBackend.PYTTSX3 == "pyttsx3"
        assert TTSBackend.GTTS == "gtts"


class TestVoiceSynthesizer:
    """Test VoiceSynthesizer class."""

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    def test_init_cpu_device(self, mock_cuda: Mock) -> None:
        """Test initialization with CPU device."""
        mock_cuda.return_value = False

        with patch.object(VoiceSynthesizer, "_initialize_backend"):
            synth = VoiceSynthesizer(backend=TTSBackend.GTTS, device="cuda")

        assert synth.device == "cpu"
        assert synth.backend == TTSBackend.GTTS
        assert synth.sample_rate == 22050

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    def test_init_cuda_device(self, mock_cuda: Mock) -> None:
        """Test initialization with CUDA device."""
        mock_cuda.return_value = True

        with patch.object(VoiceSynthesizer, "_initialize_backend"):
            synth = VoiceSynthesizer(backend=TTSBackend.GTTS, device="cuda")

        assert synth.device == "cuda"

    def test_init_unsupported_backend(self) -> None:
        """Test initialization with unsupported backend."""
        with patch("src.models.voice_synthesis.torch.cuda.is_available", return_value=False):
            with patch.object(VoiceSynthesizer, "_initialize_backend") as mock_init:
                mock_init.side_effect = ValueError("Unsupported backend: invalid")

                with pytest.raises(ValueError, match="Unsupported backend"):
                    VoiceSynthesizer(backend="invalid")  # type: ignore

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("src.models.voice_synthesis.VoiceSynthesizer._initialize_coqui")
    def test_initialize_coqui_backend(self, mock_init_coqui: Mock, mock_cuda: Mock) -> None:
        """Test Coqui backend initialization."""
        mock_cuda.return_value = False
        synth = VoiceSynthesizer(backend=TTSBackend.COQUI)
        mock_init_coqui.assert_called_once()
        assert synth.backend == TTSBackend.COQUI

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("src.models.voice_synthesis.VoiceSynthesizer._initialize_pyttsx3")
    def test_initialize_pyttsx3_backend(self, mock_init_pyttsx3: Mock, mock_cuda: Mock) -> None:
        """Test pyttsx3 backend initialization."""
        mock_cuda.return_value = False
        synth = VoiceSynthesizer(backend=TTSBackend.PYTTSX3)
        mock_init_pyttsx3.assert_called_once()
        assert synth.backend == TTSBackend.PYTTSX3

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    def test_initialize_gtts_backend(self, mock_cuda: Mock) -> None:
        """Test gTTS backend initialization."""
        mock_cuda.return_value = False
        synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        assert synth.backend == TTSBackend.GTTS
        assert synth._model is None
        assert synth._engine is None

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_initialize_coqui_with_model_path(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test Coqui initialization with custom model path."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_tts.return_value = mock_model
        synth = VoiceSynthesizer(backend=TTSBackend.COQUI, model_path="/path/to/model")
        mock_tts.assert_called_once_with(model_path="/path/to/model", gpu=False)
        assert synth._model == mock_model

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_initialize_coqui_default_model(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test Coqui initialization with default model."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_tts.return_value = mock_model
        synth = VoiceSynthesizer(backend=TTSBackend.COQUI)
        mock_tts.assert_called_once_with(
            model_name="tts_models/en/ljspeech/tacotron2-DDC", gpu=False
        )

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_initialize_coqui_import_error(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test Coqui initialization with import error."""
        mock_cuda.return_value = False
        mock_tts.side_effect = ImportError("TTS not installed")
        with pytest.raises(RuntimeError, match="Failed to import Coqui TTS"):
            VoiceSynthesizer(backend=TTSBackend.COQUI)

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("pyttsx3.init")
    def test_initialize_pyttsx3_success(self, mock_init: Mock, mock_cuda: Mock) -> None:
        """Test pyttsx3 initialization success."""
        mock_cuda.return_value = False
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        synth = VoiceSynthesizer(backend=TTSBackend.PYTTSX3)
        assert synth._engine == mock_engine
        mock_engine.setProperty.assert_any_call("rate", 150)
        mock_engine.setProperty.assert_any_call("volume", 1.0)

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("pyttsx3.init")
    def test_initialize_pyttsx3_import_error(self, mock_init: Mock, mock_cuda: Mock) -> None:
        """Test pyttsx3 initialization with import error."""
        mock_cuda.return_value = False
        mock_init.side_effect = ImportError("pyttsx3 not installed")
        with pytest.raises(RuntimeError, match="Failed to import pyttsx3"):
            VoiceSynthesizer(backend=TTSBackend.PYTTSX3)

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    def test_synthesize_empty_text(self, mock_cuda: Mock) -> None:
        """Test synthesis with empty text."""
        mock_cuda.return_value = False
        synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        with pytest.raises(ValueError, match="Text cannot be empty"):
            synth.synthesize("")

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    def test_synthesize_whitespace_text(self, mock_cuda: Mock) -> None:
        """Test synthesis with whitespace text."""
        mock_cuda.return_value = False
        synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        with pytest.raises(ValueError, match="Text cannot be empty"):
            synth.synthesize("   ")

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_synthesize_coqui_success(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test Coqui synthesis success."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_tts.return_value = mock_model
        synth = VoiceSynthesizer(backend=TTSBackend.COQUI)
        result = synth.synthesize("Hello world", "/tmp/output.wav")
        assert result == "/tmp/output.wav"
        mock_model.tts_to_file.assert_called_once_with(text="Hello world", file_path="/tmp/output.wav")

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_synthesize_coqui_with_speaker(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test Coqui synthesis with speaker wav."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_model.tts_to_file = MagicMock()
        mock_tts.return_value = mock_model
        synth = VoiceSynthesizer(backend=TTSBackend.COQUI)
        result = synth.synthesize("Hello", "/tmp/out.wav", speaker_wav="/tmp/speaker.wav")
        assert result == "/tmp/out.wav"
        mock_model.tts_to_file.assert_called_once_with(
            text="Hello", file_path="/tmp/out.wav", speaker_wav="/tmp/speaker.wav"
        )

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_synthesize_coqui_error(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test Coqui synthesis error."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_model.tts_to_file.side_effect = Exception("Synthesis failed")
        mock_tts.return_value = mock_model
        synth = VoiceSynthesizer(backend=TTSBackend.COQUI)
        with pytest.raises(RuntimeError, match="Coqui TTS synthesis failed"):
            synth.synthesize("Hello", "/tmp/out.wav")

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("pyttsx3.init")
    def test_synthesize_pyttsx3_success(self, mock_init: Mock, mock_cuda: Mock) -> None:
        """Test pyttsx3 synthesis success."""
        mock_cuda.return_value = False
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        synth = VoiceSynthesizer(backend=TTSBackend.PYTTSX3)
        result = synth.synthesize("Hello", "/tmp/out.wav")
        assert result == "/tmp/out.wav"
        mock_engine.save_to_file.assert_called_once_with("Hello", "/tmp/out.wav")
        mock_engine.runAndWait.assert_called_once()

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("pyttsx3.init")
    def test_synthesize_pyttsx3_error(self, mock_init: Mock, mock_cuda: Mock) -> None:
        """Test pyttsx3 synthesis error."""
        mock_cuda.return_value = False
        mock_engine = MagicMock()
        mock_engine.save_to_file.side_effect = Exception("Save failed")
        mock_init.return_value = mock_engine
        synth = VoiceSynthesizer(backend=TTSBackend.PYTTSX3)
        with pytest.raises(RuntimeError, match="pyttsx3 synthesis failed"):
            synth.synthesize("Hello", "/tmp/out.wav")

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("gtts.gTTS")
    def test_synthesize_gtts_success(self, mock_gtts: Mock, mock_cuda: Mock) -> None:
        """Test gTTS synthesis success."""
        mock_cuda.return_value = False
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        result = synth.synthesize("Hello", "/tmp/out.wav")
        assert result == "/tmp/out.wav"
        mock_gtts.assert_called_once_with(text="Hello", lang="en")
        mock_tts_instance.save.assert_called_once_with("/tmp/out.wav")

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("gtts.gTTS")
    def test_synthesize_gtts_import_error(self, mock_gtts: Mock, mock_cuda: Mock) -> None:
        """Test gTTS synthesis with import error."""
        mock_cuda.return_value = False
        mock_gtts.side_effect = ImportError("gTTS not installed")
        synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        with pytest.raises(RuntimeError, match="Failed to import gTTS"):
            synth.synthesize("Hello", "/tmp/out.wav")

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("gtts.gTTS")
    def test_synthesize_gtts_error(self, mock_gtts: Mock, mock_cuda: Mock) -> None:
        """Test gTTS synthesis error."""
        mock_cuda.return_value = False
        mock_tts_instance = MagicMock()
        mock_tts_instance.save.side_effect = Exception("Save failed")
        mock_gtts.return_value = mock_tts_instance
        synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        with pytest.raises(RuntimeError, match="gTTS synthesis failed"):
            synth.synthesize("Hello", "/tmp/out.wav")

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_list_available_models_coqui(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test listing Coqui models."""
        mock_cuda.return_value = False
        mock_tts.list_models.return_value = ["model1", "model2"]
        mock_tts.return_value = MagicMock()
        synth = VoiceSynthesizer(backend=TTSBackend.COQUI)
        models = synth.list_available_models()
        assert models == ["model1", "model2"]

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("pyttsx3.init")
    def test_list_available_models_pyttsx3(self, mock_init: Mock, mock_cuda: Mock) -> None:
        """Test listing pyttsx3 voices."""
        mock_cuda.return_value = False
        mock_engine = MagicMock()
        mock_voice1 = MagicMock()
        mock_voice1.name = "Voice 1"
        mock_voice2 = MagicMock()
        mock_voice2.name = "Voice 2"
        mock_engine.getProperty.return_value = [mock_voice1, mock_voice2]
        mock_init.return_value = mock_engine
        synth = VoiceSynthesizer(backend=TTSBackend.PYTTSX3)
        models = synth.list_available_models()
        assert models == ["Voice 1", "Voice 2"]

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    def test_list_available_models_gtts(self, mock_cuda: Mock) -> None:
        """Test listing gTTS languages."""
        mock_cuda.return_value = False
        synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        models = synth.list_available_models()
        assert "en" in models
        assert "es" in models
        assert "zh-CN" in models

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("pyttsx3.init")
    def test_cleanup_pyttsx3(self, mock_init: Mock, mock_cuda: Mock) -> None:
        """Test cleanup for pyttsx3."""
        mock_cuda.return_value = False
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        synth = VoiceSynthesizer(backend=TTSBackend.PYTTSX3)
        synth.cleanup()
        mock_engine.stop.assert_called_once()
        assert synth._engine is None
        assert synth._model is None

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("pyttsx3.init")
    def test_cleanup_pyttsx3_error(self, mock_init: Mock, mock_cuda: Mock) -> None:
        """Test cleanup for pyttsx3 with error."""
        mock_cuda.return_value = False
        mock_engine = MagicMock()
        mock_engine.stop.side_effect = Exception("Stop failed")
        mock_init.return_value = mock_engine
        synth = VoiceSynthesizer(backend=TTSBackend.PYTTSX3)
        synth.cleanup()  # Should not raise
        assert synth._engine is None

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    def test_cleanup_gtts(self, mock_cuda: Mock) -> None:
        """Test cleanup for gTTS."""
        mock_cuda.return_value = False
        synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        synth.cleanup()
        assert synth._engine is None
        assert synth._model is None

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_synthesize_with_temp_file(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test synthesis with temporary file."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_tts.return_value = mock_model
        synth = VoiceSynthesizer(backend=TTSBackend.COQUI)
        result = synth.synthesize("Hello")
        assert result.endswith(".wav")
        mock_model.tts_to_file.assert_called_once()

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_initialize_coqui_runtime_error(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test Coqui initialization with runtime error."""
        mock_cuda.return_value = False
        mock_tts.side_effect = Exception("Model load failed")
        with pytest.raises(RuntimeError, match="Failed to initialize Coqui TTS"):
            VoiceSynthesizer(backend=TTSBackend.COQUI)

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("pyttsx3.init")
    def test_initialize_pyttsx3_runtime_error(self, mock_init: Mock, mock_cuda: Mock) -> None:
        """Test pyttsx3 initialization with runtime error."""
        mock_cuda.return_value = False
        mock_init.side_effect = Exception("Engine init failed")
        with pytest.raises(RuntimeError, match="Failed to initialize pyttsx3"):
            VoiceSynthesizer(backend=TTSBackend.PYTTSX3)

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_synthesize_coqui_without_speaker(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test Coqui synthesis without speaker wav (standard TTS)."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        # Remove tts_to_file attribute to test standard TTS path
        del mock_model.tts_to_file
        mock_model.tts_to_file = MagicMock()
        mock_tts.return_value = mock_model
        synth = VoiceSynthesizer(backend=TTSBackend.COQUI)
        result = synth.synthesize("Hello", "/tmp/out.wav")
        assert result == "/tmp/out.wav"

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("pyttsx3.init")
    def test_synthesize_pyttsx3_no_engine(self, mock_init: Mock, mock_cuda: Mock) -> None:
        """Test pyttsx3 synthesis with no engine."""
        mock_cuda.return_value = False
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        synth = VoiceSynthesizer(backend=TTSBackend.PYTTSX3)
        synth._engine = None
        with pytest.raises(RuntimeError, match="pyttsx3 engine not initialized"):
            synth.synthesize("Hello", "/tmp/out.wav")

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("TTS.api.TTS")
    def test_list_available_models_coqui_error(self, mock_tts: Mock, mock_cuda: Mock) -> None:
        """Test listing Coqui models with error."""
        mock_cuda.return_value = False
        mock_tts.list_models.side_effect = Exception("List failed")
        mock_tts.return_value = MagicMock()
        synth = VoiceSynthesizer(backend=TTSBackend.COQUI)
        with pytest.raises(RuntimeError, match="Failed to list Coqui models"):
            synth.list_available_models()

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    @patch("pyttsx3.init")
    def test_list_available_models_pyttsx3_no_engine(self, mock_init: Mock, mock_cuda: Mock) -> None:
        """Test listing pyttsx3 models with no engine."""
        mock_cuda.return_value = False
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        synth = VoiceSynthesizer(backend=TTSBackend.PYTTSX3)
        synth._engine = None
        models = synth.list_available_models()
        assert models == []

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    def test_unsupported_backend_in_initialize(self, mock_cuda: Mock) -> None:
        """Test unsupported backend in _initialize_backend."""
        mock_cuda.return_value = False
        with patch.object(VoiceSynthesizer, "_initialize_backend"):
            synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        # Manually set an invalid backend
        synth.backend = "invalid"  # type: ignore
        with pytest.raises(ValueError, match="Unsupported backend"):
            synth._initialize_backend()

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    def test_unsupported_backend_in_synthesize(self, mock_cuda: Mock) -> None:
        """Test unsupported backend in synthesize."""
        mock_cuda.return_value = False
        with patch.object(VoiceSynthesizer, "_initialize_backend"):
            synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        # Manually set an invalid backend
        synth.backend = "invalid"  # type: ignore
        with pytest.raises(RuntimeError, match="Backend invalid not initialized"):
            synth.synthesize("Hello", "/tmp/out.wav")

    @patch("src.models.voice_synthesis.torch.cuda.is_available")
    def test_unsupported_backend_in_list_models(self, mock_cuda: Mock) -> None:
        """Test unsupported backend in list_available_models."""
        mock_cuda.return_value = False
        with patch.object(VoiceSynthesizer, "_initialize_backend"):
            synth = VoiceSynthesizer(backend=TTSBackend.GTTS)
        # Manually set an invalid backend
        synth.backend = "invalid"  # type: ignore
        with pytest.raises(RuntimeError, match="Backend invalid doesn't support model listing"):
            synth.list_available_models()
