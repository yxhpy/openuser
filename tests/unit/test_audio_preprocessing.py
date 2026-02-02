"""Tests for Audio Preprocessing module"""

import os
import tempfile
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
import torch

from src.models.audio_preprocessing import AudioPreprocessor, AudioFormat


@pytest.fixture
def audio_preprocessor():
    """Create AudioPreprocessor instance"""
    return AudioPreprocessor(sample_rate=16000, normalize=True)


@pytest.fixture
def sample_audio():
    """Create sample audio data"""
    # Generate 1 second of sine wave at 440 Hz
    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration))
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    return audio.astype(np.float32), sr


@pytest.fixture
def temp_audio_file(sample_audio):
    """Create temporary audio file"""
    audio_data, sr = sample_audio
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name

    # Mock soundfile to save audio
    with patch("soundfile.write") as mock_write:
        mock_write.return_value = None
        # Create the file
        with open(temp_path, "wb") as f:
            f.write(b"fake audio data")

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_audio_preprocessor_init():
    """Test AudioPreprocessor initialization"""
    preprocessor = AudioPreprocessor(sample_rate=22050, normalize=False)

    assert preprocessor.sample_rate == 22050
    assert preprocessor.normalize is False


def test_audio_preprocessor_device_selection():
    """Test device selection based on CUDA availability"""
    with patch("torch.cuda.is_available", return_value=True):
        preprocessor = AudioPreprocessor(device="cuda")
        assert preprocessor.device == "cuda"

    with patch("torch.cuda.is_available", return_value=False):
        preprocessor = AudioPreprocessor(device="cuda")
        assert preprocessor.device == "cpu"


def test_load_audio_success(audio_preprocessor, temp_audio_file):
    """Test successful audio loading"""
    with patch("librosa.load") as mock_load:
        mock_load.return_value = (np.array([0.1, 0.2, 0.3]), 16000)

        audio_data, sr = audio_preprocessor.load_audio(temp_audio_file)

        assert len(audio_data) == 3
        assert sr == 16000
        mock_load.assert_called_once()


def test_load_audio_file_not_found(audio_preprocessor):
    """Test loading non-existent audio file"""
    with pytest.raises(FileNotFoundError, match="Audio file not found"):
        audio_preprocessor.load_audio("/nonexistent/audio.wav")


def test_load_audio_import_error(audio_preprocessor, temp_audio_file):
    """Test audio loading with import error"""
    with patch("librosa.load", side_effect=ImportError("librosa not found")):
        with pytest.raises(RuntimeError, match="Failed to import librosa"):
            audio_preprocessor.load_audio(temp_audio_file)


def test_load_audio_runtime_error(audio_preprocessor, temp_audio_file):
    """Test audio loading with runtime error"""
    with patch("librosa.load", side_effect=Exception("Load error")):
        with pytest.raises(RuntimeError, match="Failed to load audio"):
            audio_preprocessor.load_audio(temp_audio_file)


def test_convert_sample_rate_no_change(audio_preprocessor, sample_audio):
    """Test sample rate conversion when rates are the same"""
    audio_data, sr = sample_audio

    result = audio_preprocessor.convert_sample_rate(audio_data, sr, sr)

    assert np.array_equal(result, audio_data)


def test_convert_sample_rate_success(audio_preprocessor, sample_audio):
    """Test successful sample rate conversion"""
    audio_data, sr = sample_audio

    with patch("librosa.resample") as mock_resample:
        mock_resample.return_value = np.array([0.1, 0.2])

        result = audio_preprocessor.convert_sample_rate(audio_data, sr, 8000)

        assert len(result) == 2
        mock_resample.assert_called_once()


def test_convert_sample_rate_default_target(audio_preprocessor, sample_audio):
    """Test sample rate conversion with default target"""
    audio_data, sr = sample_audio

    with patch("librosa.resample") as mock_resample:
        mock_resample.return_value = audio_data

        # Use a different source sample rate to trigger resampling
        audio_preprocessor.convert_sample_rate(audio_data, 22050, None)

        # Should use self.sample_rate as target
        mock_resample.assert_called_once_with(
            audio_data, orig_sr=22050, target_sr=audio_preprocessor.sample_rate
        )


def test_convert_sample_rate_error(audio_preprocessor, sample_audio):
    """Test sample rate conversion error"""
    audio_data, sr = sample_audio

    with patch("librosa.resample", side_effect=Exception("Resample error")):
        with pytest.raises(RuntimeError, match="Failed to resample audio"):
            audio_preprocessor.convert_sample_rate(audio_data, sr, 8000)


def test_normalize_audio(audio_preprocessor):
    """Test audio normalization"""
    # Create audio with known RMS
    audio_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

    normalized = audio_preprocessor.normalize_audio(audio_data, target_db=-20.0)

    # Check that audio is normalized
    assert len(normalized) == len(audio_data)
    assert np.all(np.abs(normalized) <= 1.0)


def test_normalize_audio_silent(audio_preprocessor):
    """Test normalizing silent audio"""
    audio_data = np.zeros(100)

    normalized = audio_preprocessor.normalize_audio(audio_data)

    # Silent audio should remain silent
    assert np.array_equal(normalized, audio_data)


def test_normalize_audio_clipping(audio_preprocessor):
    """Test that normalization clips values"""
    # Create audio that would exceed [-1, 1] after normalization
    audio_data = np.array([0.1, 0.2, 0.3])

    normalized = audio_preprocessor.normalize_audio(audio_data, target_db=20.0)

    # All values should be clipped to [-1, 1]
    assert np.all(normalized >= -1.0)
    assert np.all(normalized <= 1.0)


def test_trim_silence_success(audio_preprocessor, sample_audio):
    """Test successful silence trimming"""
    audio_data, sr = sample_audio

    with patch("librosa.effects.trim") as mock_trim:
        mock_trim.return_value = (audio_data[:500], None)

        trimmed = audio_preprocessor.trim_silence(audio_data)

        assert len(trimmed) == 500
        mock_trim.assert_called_once()


def test_trim_silence_error(audio_preprocessor, sample_audio):
    """Test silence trimming error"""
    audio_data, sr = sample_audio

    with patch("librosa.effects.trim", side_effect=Exception("Trim error")):
        with pytest.raises(RuntimeError, match="Failed to trim silence"):
            audio_preprocessor.trim_silence(audio_data)


def test_reduce_noise_success(audio_preprocessor, sample_audio):
    """Test successful noise reduction"""
    audio_data, sr = sample_audio

    # Create a mock module
    mock_nr = MagicMock()
    mock_nr.reduce_noise.return_value = audio_data * 0.9

    with patch.dict("sys.modules", {"noisereduce": mock_nr}):
        reduced = audio_preprocessor.reduce_noise(audio_data, sr, 0.5)

        assert len(reduced) == len(audio_data)
        mock_nr.reduce_noise.assert_called_once()


def test_reduce_noise_import_error(audio_preprocessor, sample_audio):
    """Test noise reduction when noisereduce not available"""
    audio_data, sr = sample_audio

    # Mock the import to raise ImportError
    with patch("builtins.__import__", side_effect=ImportError("No module named 'noisereduce'")):
        # Should return original audio when noisereduce not available
        reduced = audio_preprocessor.reduce_noise(audio_data, sr)

        assert np.array_equal(reduced, audio_data)


def test_reduce_noise_error(audio_preprocessor, sample_audio):
    """Test noise reduction error"""
    audio_data, sr = sample_audio

    # Create a mock module that raises an exception
    mock_nr = MagicMock()
    mock_nr.reduce_noise.side_effect = Exception("Reduce error")

    with patch.dict("sys.modules", {"noisereduce": mock_nr}):
        with pytest.raises(RuntimeError, match="Failed to reduce noise"):
            audio_preprocessor.reduce_noise(audio_data, sr)


def test_save_audio_success(audio_preprocessor, sample_audio):
    """Test successful audio saving"""
    audio_data, sr = sample_audio

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        output_path = f.name

    try:
        with patch("soundfile.write") as mock_write:
            mock_write.return_value = None

            result = audio_preprocessor.save_audio(audio_data, output_path, sr)

            assert result == output_path
            mock_write.assert_called_once()
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_save_audio_default_sr(audio_preprocessor, sample_audio):
    """Test saving audio with default sample rate"""
    audio_data, sr = sample_audio

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        output_path = f.name

    try:
        with patch("soundfile.write") as mock_write:
            mock_write.return_value = None

            audio_preprocessor.save_audio(audio_data, output_path, None)

            # Should use self.sample_rate
            mock_write.assert_called_once_with(
                output_path, audio_data, audio_preprocessor.sample_rate
            )
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_save_audio_import_error(audio_preprocessor, sample_audio):
    """Test audio saving with import error"""
    audio_data, sr = sample_audio

    with patch("soundfile.write", side_effect=ImportError("soundfile not found")):
        with pytest.raises(RuntimeError, match="Failed to import soundfile"):
            audio_preprocessor.save_audio(audio_data, "output.wav", sr)


def test_save_audio_runtime_error(audio_preprocessor, sample_audio):
    """Test audio saving with runtime error"""
    audio_data, sr = sample_audio

    with patch("soundfile.write", side_effect=Exception("Write error")):
        with pytest.raises(RuntimeError, match="Failed to save audio"):
            audio_preprocessor.save_audio(audio_data, "output.wav", sr)


def test_convert_format_success(audio_preprocessor, temp_audio_file):
    """Test successful format conversion"""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        output_path = f.name

    try:
        with patch.object(audio_preprocessor, "load_audio") as mock_load:
            with patch.object(audio_preprocessor, "save_audio") as mock_save:
                mock_load.return_value = (np.array([0.1, 0.2]), 16000)
                mock_save.return_value = output_path

                result = audio_preprocessor.convert_format(
                    temp_audio_file, output_path, AudioFormat.MP3
                )

                assert result == output_path
                assert output_path.endswith(".mp3")
                mock_load.assert_called_once()
                mock_save.assert_called_once()
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_validate_audio_quality(audio_preprocessor, sample_audio):
    """Test audio quality validation"""
    audio_data, sr = sample_audio

    metrics = audio_preprocessor.validate_audio_quality(audio_data, sr)

    assert "duration" in metrics
    assert "sample_rate" in metrics
    assert "num_samples" in metrics
    assert "rms" in metrics
    assert "peak" in metrics
    assert "is_clipped" in metrics
    assert "is_silent" in metrics

    assert metrics["sample_rate"] == sr
    assert metrics["num_samples"] == len(audio_data)
    assert metrics["duration"] == len(audio_data) / sr
    assert metrics["is_clipped"] is False
    assert metrics["is_silent"] is False


def test_validate_audio_quality_clipped():
    """Test quality validation with clipped audio"""
    preprocessor = AudioPreprocessor()
    audio_data = np.array([0.5, 0.99, 1.0, 0.5])  # Contains clipped value

    metrics = preprocessor.validate_audio_quality(audio_data, 16000)

    assert metrics["is_clipped"] is True


def test_validate_audio_quality_silent():
    """Test quality validation with silent audio"""
    preprocessor = AudioPreprocessor()
    audio_data = np.array([0.001, 0.002, 0.001])  # Very quiet

    metrics = preprocessor.validate_audio_quality(audio_data, 16000)

    assert metrics["is_silent"] is True


def test_preprocess_full_pipeline(audio_preprocessor, temp_audio_file):
    """Test full preprocessing pipeline"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        output_path = f.name

    try:
        with patch.object(audio_preprocessor, "load_audio") as mock_load:
            with patch.object(audio_preprocessor, "convert_sample_rate") as mock_convert:
                with patch.object(audio_preprocessor, "trim_silence") as mock_trim:
                    with patch.object(audio_preprocessor, "normalize_audio") as mock_normalize:
                        with patch.object(audio_preprocessor, "save_audio") as mock_save:
                            audio_data = np.array([0.1, 0.2, 0.3])
                            mock_load.return_value = (audio_data, 16000)
                            mock_convert.return_value = audio_data
                            mock_trim.return_value = audio_data
                            mock_normalize.return_value = audio_data
                            mock_save.return_value = output_path

                            result_path, metrics = audio_preprocessor.preprocess(
                                temp_audio_file, output_path
                            )

                            assert result_path == output_path
                            assert "duration" in metrics
                            mock_load.assert_called_once()
                            mock_convert.assert_called_once()
                            mock_trim.assert_called_once()
                            mock_normalize.assert_called_once()
                            mock_save.assert_called_once()
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_preprocess_with_noise_reduction(audio_preprocessor, temp_audio_file):
    """Test preprocessing with noise reduction enabled"""
    with patch.object(audio_preprocessor, "load_audio") as mock_load:
        with patch.object(audio_preprocessor, "convert_sample_rate") as mock_convert:
            with patch.object(audio_preprocessor, "trim_silence") as mock_trim:
                with patch.object(audio_preprocessor, "reduce_noise") as mock_reduce:
                    with patch.object(audio_preprocessor, "normalize_audio") as mock_normalize:
                        with patch.object(audio_preprocessor, "save_audio") as mock_save:
                            audio_data = np.array([0.1, 0.2, 0.3])
                            mock_load.return_value = (audio_data, 16000)
                            mock_convert.return_value = audio_data
                            mock_trim.return_value = audio_data
                            mock_reduce.return_value = audio_data
                            mock_normalize.return_value = audio_data
                            mock_save.return_value = "output.wav"

                            audio_preprocessor.preprocess(
                                temp_audio_file, reduce_noise=True, noise_strength=0.7
                            )

                            mock_reduce.assert_called_once()


def test_preprocess_without_normalization(audio_preprocessor, temp_audio_file):
    """Test preprocessing without normalization"""
    with patch.object(audio_preprocessor, "load_audio") as mock_load:
        with patch.object(audio_preprocessor, "convert_sample_rate") as mock_convert:
            with patch.object(audio_preprocessor, "trim_silence") as mock_trim:
                with patch.object(audio_preprocessor, "normalize_audio") as mock_normalize:
                    with patch.object(audio_preprocessor, "save_audio") as mock_save:
                        audio_data = np.array([0.1, 0.2, 0.3])
                        mock_load.return_value = (audio_data, 16000)
                        mock_convert.return_value = audio_data
                        mock_trim.return_value = audio_data
                        mock_save.return_value = "output.wav"

                        audio_preprocessor.preprocess(temp_audio_file, normalize=False)

                        mock_normalize.assert_not_called()


def test_preprocess_without_trim_silence(audio_preprocessor, temp_audio_file):
    """Test preprocessing without silence trimming"""
    with patch.object(audio_preprocessor, "load_audio") as mock_load:
        with patch.object(audio_preprocessor, "convert_sample_rate") as mock_convert:
            with patch.object(audio_preprocessor, "trim_silence") as mock_trim:
                with patch.object(audio_preprocessor, "normalize_audio") as mock_normalize:
                    with patch.object(audio_preprocessor, "save_audio") as mock_save:
                        audio_data = np.array([0.1, 0.2, 0.3])
                        mock_load.return_value = (audio_data, 16000)
                        mock_convert.return_value = audio_data
                        mock_normalize.return_value = audio_data
                        mock_save.return_value = "output.wav"

                        audio_preprocessor.preprocess(temp_audio_file, trim_silence=False)

                        mock_trim.assert_not_called()


def test_preprocess_creates_temp_file(audio_preprocessor, temp_audio_file):
    """Test preprocessing creates temp file when output_path is None"""
    with patch.object(audio_preprocessor, "load_audio") as mock_load:
        with patch.object(audio_preprocessor, "convert_sample_rate") as mock_convert:
            with patch.object(audio_preprocessor, "trim_silence") as mock_trim:
                with patch.object(audio_preprocessor, "normalize_audio") as mock_normalize:
                    with patch.object(audio_preprocessor, "save_audio") as mock_save:
                        audio_data = np.array([0.1, 0.2, 0.3])
                        mock_load.return_value = (audio_data, 16000)
                        mock_convert.return_value = audio_data
                        mock_trim.return_value = audio_data
                        mock_normalize.return_value = audio_data
                        mock_save.return_value = "/tmp/temp_audio.wav"

                        result_path, _ = audio_preprocessor.preprocess(temp_audio_file)

                        # Should create a temp file
                        assert result_path is not None
                        mock_save.assert_called_once()






