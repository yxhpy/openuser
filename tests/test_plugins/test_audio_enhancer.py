"""
Tests for Audio Enhancer Plugin
"""

import pytest
import tempfile
import os
from pathlib import Path
import numpy as np
import soundfile as sf

from src.plugins.audio_enhancer import AudioEnhancer
from src.core.plugin_config import PluginConfig


@pytest.fixture
def audio_enhancer():
    """Create audio enhancer plugin instance"""
    plugin = AudioEnhancer()
    plugin.on_load()
    yield plugin
    plugin.on_unload()


@pytest.fixture
def sample_audio_file():
    """Create a sample audio file for testing"""
    # Generate 1 second of audio at 22050 Hz
    sample_rate = 22050
    duration = 1.0
    frequency = 440.0  # A4 note

    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)

    # Add some noise
    noise = np.random.normal(0, 0.05, audio_data.shape)
    audio_data = audio_data + noise

    # Create temp file
    temp_file = tempfile.mktemp(suffix=".wav")
    sf.write(temp_file, audio_data, sample_rate)

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_plugin_initialization():
    """Test plugin initialization"""
    plugin = AudioEnhancer()
    assert plugin.name == "audio_enhancer"
    assert plugin.version == "1.0.0"
    assert plugin.dependencies == []


def test_plugin_load_unload():
    """Test plugin load and unload"""
    plugin = AudioEnhancer()
    plugin.on_load()
    assert plugin._preprocessor is not None
    plugin.on_unload()
    assert plugin._preprocessor is None


def test_denoise(audio_enhancer, sample_audio_file):
    """Test audio denoising"""
    output_path = tempfile.mktemp(suffix=".wav")

    try:
        result = audio_enhancer.denoise(sample_audio_file, output_path)
        assert result == output_path
        assert os.path.exists(output_path)

        # Verify output is valid audio
        audio_data, sr = sf.read(output_path)
        assert len(audio_data) > 0
        assert sr > 0
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


def test_denoise_with_custom_strength(audio_enhancer, sample_audio_file):
    """Test audio denoising with custom strength"""
    output_path = tempfile.mktemp(suffix=".wav")

    try:
        result = audio_enhancer.denoise(sample_audio_file, output_path, strength=0.8)
        assert result == output_path
        assert os.path.exists(output_path)
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


def test_denoise_auto_output(audio_enhancer, sample_audio_file):
    """Test audio denoising with automatic output path"""
    result = audio_enhancer.denoise(sample_audio_file)
    try:
        assert os.path.exists(result)
        assert result.endswith(".wav")
    finally:
        if os.path.exists(result):
            os.remove(result)


def test_normalize(audio_enhancer, sample_audio_file):
    """Test audio normalization"""
    output_path = tempfile.mktemp(suffix=".wav")

    try:
        result = audio_enhancer.normalize(sample_audio_file, output_path)
        assert result == output_path
        assert os.path.exists(output_path)

        # Verify output is valid audio
        audio_data, sr = sf.read(output_path)
        assert len(audio_data) > 0
        assert sr > 0
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


def test_normalize_with_target_db(audio_enhancer, sample_audio_file):
    """Test audio normalization with custom target dB"""
    output_path = tempfile.mktemp(suffix=".wav")

    try:
        result = audio_enhancer.normalize(sample_audio_file, output_path, target_db=-15.0)
        assert result == output_path
        assert os.path.exists(output_path)
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


def test_enhance(audio_enhancer, sample_audio_file):
    """Test full audio enhancement"""
    output_path = tempfile.mktemp(suffix=".wav")

    try:
        result = audio_enhancer.enhance(sample_audio_file, output_path)
        assert "output_path" in result
        assert "metrics" in result
        assert result["output_path"] == output_path
        assert os.path.exists(output_path)

        # Verify metrics
        metrics = result["metrics"]
        assert "duration" in metrics
        assert "sample_rate" in metrics
        assert "rms" in metrics
        assert "peak" in metrics
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


def test_enhance_with_options(audio_enhancer, sample_audio_file):
    """Test audio enhancement with custom options"""
    output_path = tempfile.mktemp(suffix=".wav")

    try:
        result = audio_enhancer.enhance(
            sample_audio_file,
            output_path,
            denoise=True,
            normalize=True,
            trim_silence=False,
            noise_strength=0.7,
            target_db=-18.0
        )
        assert result["output_path"] == output_path
        assert os.path.exists(output_path)
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


def test_enhance_auto_output(audio_enhancer, sample_audio_file):
    """Test audio enhancement with automatic output path"""
    result = audio_enhancer.enhance(sample_audio_file)
    try:
        assert "output_path" in result
        assert os.path.exists(result["output_path"])
    finally:
        if os.path.exists(result["output_path"]):
            os.remove(result["output_path"])


def test_get_stats(audio_enhancer, sample_audio_file):
    """Test getting plugin statistics"""
    # Process some files
    output1 = audio_enhancer.denoise(sample_audio_file)
    output2 = audio_enhancer.normalize(sample_audio_file)

    try:
        stats = audio_enhancer.get_stats()
        assert "processed_count" in stats
        assert stats["processed_count"] == 2
        assert "sample_rate" in stats
        assert "normalize" in stats
        assert "noise_reduce_strength" in stats
    finally:
        if os.path.exists(output1):
            os.remove(output1)
        if os.path.exists(output2):
            os.remove(output2)


def test_plugin_not_loaded():
    """Test operations when plugin is not loaded"""
    plugin = AudioEnhancer()

    with pytest.raises(RuntimeError, match="Plugin not loaded"):
        plugin.denoise("test.wav")

    with pytest.raises(RuntimeError, match="Plugin not loaded"):
        plugin.normalize("test.wav")

    with pytest.raises(RuntimeError, match="Plugin not loaded"):
        plugin.enhance("test.wav")


def test_invalid_input_file(audio_enhancer):
    """Test with non-existent input file"""
    with pytest.raises(FileNotFoundError):
        audio_enhancer.denoise("nonexistent.wav")

    with pytest.raises(FileNotFoundError):
        audio_enhancer.normalize("nonexistent.wav")

    with pytest.raises(FileNotFoundError):
        audio_enhancer.enhance("nonexistent.wav")


def test_config_schema():
    """Test plugin configuration schema"""
    plugin = AudioEnhancer()
    schema = plugin.config_schema

    # Check that fields exist
    field_names = [f.name for f in schema.fields]
    assert "sample_rate" in field_names
    assert "normalize" in field_names
    assert "noise_reduce_strength" in field_names

    # Test field defaults
    defaults = schema.get_defaults()
    assert defaults["sample_rate"] == 22050
    assert defaults["normalize"] is True
    assert defaults["noise_reduce_strength"] == 0.5


def test_custom_config():
    """Test plugin with custom configuration"""
    plugin = AudioEnhancer()

    # Create custom config
    config = PluginConfig("audio_enhancer", plugin.config_schema)
    config.set("sample_rate", 44100)
    config.set("normalize", False)
    config.set("noise_reduce_strength", 0.8)

    plugin.config = config

    plugin.on_load()

    try:
        assert plugin._get_config("sample_rate", 22050) == 44100
        assert plugin._get_config("normalize", True) is False
        assert plugin._get_config("noise_reduce_strength", 0.5) == 0.8
    finally:
        plugin.on_unload()


def test_state_tracking(audio_enhancer, sample_audio_file):
    """Test that plugin tracks state correctly"""
    initial_count = audio_enhancer._state["processed_count"]

    output1 = audio_enhancer.denoise(sample_audio_file)
    assert audio_enhancer._state["processed_count"] == initial_count + 1

    output2 = audio_enhancer.normalize(sample_audio_file)
    assert audio_enhancer._state["processed_count"] == initial_count + 2

    result = audio_enhancer.enhance(sample_audio_file)
    assert audio_enhancer._state["processed_count"] == initial_count + 3

    # Cleanup
    for path in [output1, output2, result["output_path"]]:
        if os.path.exists(path):
            os.remove(path)


