"""
Audio Enhancer Plugin

Provides audio enhancement and noise reduction capabilities.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import tempfile

from src.core.plugin_manager import Plugin
from src.core.plugin_config import (
    PluginConfigSchema,
    ConfigField,
    ConfigFieldType,
)


class AudioEnhancer(Plugin):
    """Audio enhancement plugin"""

    name = "audio_enhancer"
    version = "1.0.0"
    dependencies = []

    # Define configuration schema
    config_schema = PluginConfigSchema()
    config_schema.add_field(ConfigField(
        name="sample_rate",
        field_type=ConfigFieldType.INTEGER,
        default=22050,
        description="Target sample rate for audio processing",
        validator=lambda x: x > 0
    ))
    config_schema.add_field(ConfigField(
        name="normalize",
        field_type=ConfigFieldType.BOOLEAN,
        default=True,
        description="Whether to normalize audio by default"
    ))
    config_schema.add_field(ConfigField(
        name="noise_reduce_strength",
        field_type=ConfigFieldType.FLOAT,
        default=0.5,
        description="Default noise reduction strength (0.0 to 1.0)",
        validator=lambda x: 0.0 <= x <= 1.0
    ))

    def __init__(self) -> None:
        super().__init__()
        self._state["processed_count"] = 0
        self._preprocessor = None

    def _get_config(self, key: str, default: Any) -> Any:
        """Helper to get config value safely"""
        if self.config:
            return self.config.get(key, default)
        return default

    def on_load(self) -> None:
        """Called when plugin is loaded"""
        super().on_load()

        # Import here to avoid dependency issues
        from src.models.audio_preprocessing import AudioPreprocessor

        sample_rate = self._get_config("sample_rate", 22050)
        normalize = self._get_config("normalize", True)

        self._preprocessor = AudioPreprocessor(
            sample_rate=sample_rate,
            device="cpu",
            normalize=normalize
        )

        self.logger.info(
            f"Audio enhancer plugin loaded. "
            f"Sample rate: {sample_rate}, Normalize: {normalize}"
        )

    def on_unload(self) -> None:
        """Called when plugin is unloaded"""
        super().on_unload()
        count = self._state["processed_count"]
        self.logger.info(
            f"Audio enhancer plugin unloaded. "
            f"Processed {count} audio files"
        )
        self._preprocessor = None

    def denoise(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        strength: Optional[float] = None
    ) -> str:
        """
        Reduce noise from audio file.

        Args:
            input_path: Path to input audio file
            output_path: Path to output audio file (creates temp file if None)
            strength: Noise reduction strength (0.0 to 1.0, uses config default if None)

        Returns:
            Path to denoised audio file

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If denoising fails
        """
        if not self._preprocessor:
            raise RuntimeError("Plugin not loaded")

        if strength is None:
            strength = self._get_config("noise_reduce_strength", 0.5)

        # Load audio
        audio_data, sr = self._preprocessor.load_audio(input_path)

        # Reduce noise
        audio_data = self._preprocessor.reduce_noise(audio_data, sr, strength)

        # Save audio
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav")

        output_path = self._preprocessor.save_audio(audio_data, output_path, sr)

        self._state["processed_count"] += 1
        self.logger.info(f"Denoised audio: {input_path} -> {output_path}")

        return output_path

    def normalize(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        target_db: float = -20.0
    ) -> str:
        """
        Normalize audio to target dB level.

        Args:
            input_path: Path to input audio file
            output_path: Path to output audio file (creates temp file if None)
            target_db: Target dB level

        Returns:
            Path to normalized audio file

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If normalization fails
        """
        if not self._preprocessor:
            raise RuntimeError("Plugin not loaded")

        # Load audio
        audio_data, sr = self._preprocessor.load_audio(input_path)

        # Normalize
        audio_data = self._preprocessor.normalize_audio(audio_data, target_db)

        # Save audio
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".wav")

        output_path = self._preprocessor.save_audio(audio_data, output_path, sr)

        self._state["processed_count"] += 1
        self.logger.info(f"Normalized audio: {input_path} -> {output_path}")

        return output_path

    def enhance(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        denoise: bool = True,
        normalize: bool = True,
        trim_silence: bool = True,
        noise_strength: Optional[float] = None,
        target_db: float = -20.0
    ) -> Dict[str, Any]:
        """
        Enhance audio with multiple processing steps.

        Args:
            input_path: Path to input audio file
            output_path: Path to output audio file (creates temp file if None)
            denoise: Whether to reduce noise
            normalize: Whether to normalize audio
            trim_silence: Whether to trim silence
            noise_strength: Noise reduction strength (uses config default if None)
            target_db: Target dB level for normalization

        Returns:
            Dictionary with output_path and quality metrics

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If enhancement fails
        """
        if not self._preprocessor:
            raise RuntimeError("Plugin not loaded")

        if noise_strength is None:
            noise_strength = self._get_config("noise_reduce_strength", 0.5)

        # Use preprocessor's full pipeline
        output_path, metrics = self._preprocessor.preprocess(
            input_path=input_path,
            output_path=output_path,
            target_sr=self._get_config("sample_rate", 22050),
            normalize=normalize,
            trim_silence=trim_silence,
            reduce_noise=denoise,
            noise_strength=noise_strength
        )

        self._state["processed_count"] += 1
        self.logger.info(f"Enhanced audio: {input_path} -> {output_path}")

        return {
            "output_path": output_path,
            "metrics": metrics
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get plugin statistics.

        Returns:
            Dictionary with plugin statistics
        """
        return {
            "processed_count": self._state["processed_count"],
            "sample_rate": self._get_config("sample_rate", 22050),
            "normalize": self._get_config("normalize", True),
            "noise_reduce_strength": self._get_config("noise_reduce_strength", 0.5)
        }

