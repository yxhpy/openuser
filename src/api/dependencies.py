"""
Dependency injection for FastAPI endpoints.
"""
from functools import lru_cache
from typing import Optional
import os

from src.models.voice_synthesis import VoiceSynthesizer
from src.models.voice_cloning import VoiceCloner


@lru_cache()
def get_voice_synthesizer(
    backend: str = "coqui",
    device: str = "cpu",
    model_path: Optional[str] = None,
    sample_rate: int = 22050
) -> VoiceSynthesizer:
    """
    Get or create VoiceSynthesizer instance.

    Uses LRU cache to reuse instances with same parameters.
    """
    return VoiceSynthesizer(
        backend=backend,
        device=device,
        model_path=model_path,
        sample_rate=sample_rate
    )


@lru_cache()
def get_voice_cloner(
    profile_dir: Optional[str] = None,
    device: str = "cpu",
    min_samples: int = 3,
    sample_rate: int = 22050
) -> VoiceCloner:
    """
    Get or create VoiceCloner instance.

    Uses LRU cache to reuse instances with same parameters.
    """
    if profile_dir is None:
        profile_dir = os.path.join(os.getcwd(), "voice_profiles")

    return VoiceCloner(
        profile_dir=profile_dir,
        device=device,
        min_samples=min_samples,
        sample_rate=sample_rate
    )
