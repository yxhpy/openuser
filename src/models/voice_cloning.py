"""
Voice cloning module for creating personalized voice models.

This module provides voice cloning functionality including:
- Voice sample collection and validation
- Audio preprocessing and enhancement
- Voice profile creation and management
- Integration with TTS models for voice cloning

Features:
- Multi-sample voice profile creation
- Audio quality validation
- Voice embedding extraction
- Profile persistence and loading
"""

import json
import os
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

import torch
import numpy as np


@dataclass
class VoiceProfile:
    """Voice profile containing voice characteristics and metadata."""

    name: str
    description: str
    sample_paths: List[str]
    embedding_path: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize timestamps and metadata."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class VoiceCloner:
    """
    Voice cloning system for creating personalized voice models.

    Attributes:
        profile_dir: Directory to store voice profiles
        device: Device for model inference (cpu/cuda)
        min_samples: Minimum number of voice samples required
        sample_rate: Audio sample rate
    """

    def __init__(
        self,
        profile_dir: str = "voice_profiles",
        device: str = "cpu",
        min_samples: int = 3,
        sample_rate: int = 22050,
    ) -> None:
        """
        Initialize voice cloner.

        Args:
            profile_dir: Directory to store voice profiles
            device: Device for model inference (cpu/cuda)
            min_samples: Minimum number of voice samples required
            sample_rate: Audio sample rate
        """
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.device = device if torch.cuda.is_available() else "cpu"
        self.min_samples = min_samples
        self.sample_rate = sample_rate

    def validate_audio_samples(self, sample_paths: List[str]) -> bool:
        """
        Validate audio samples for voice cloning.

        Args:
            sample_paths: List of paths to audio samples

        Returns:
            True if samples are valid

        Raises:
            ValueError: If samples are invalid
        """
        if len(sample_paths) < self.min_samples:
            raise ValueError(
                f"At least {self.min_samples} samples required, got {len(sample_paths)}"
            )

        for path in sample_paths:
            if not os.path.exists(path):
                raise ValueError(f"Sample file not found: {path}")

            # Check file extension
            if not path.lower().endswith((".wav", ".mp3", ".flac", ".ogg")):
                raise ValueError(f"Unsupported audio format: {path}")

        return True

    def create_profile(
        self,
        name: str,
        sample_paths: List[str],
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VoiceProfile:
        """
        Create a voice profile from audio samples.

        Args:
            name: Profile name
            sample_paths: List of paths to audio samples
            description: Profile description
            metadata: Additional metadata

        Returns:
            Created voice profile

        Raises:
            ValueError: If samples are invalid or profile exists
        """
        # Validate samples
        self.validate_audio_samples(sample_paths)

        # Check if profile already exists
        profile_path = self.profile_dir / f"{name}.json"
        if profile_path.exists():
            raise ValueError(f"Profile '{name}' already exists")

        # Create profile
        profile = VoiceProfile(
            name=name,
            description=description,
            sample_paths=sample_paths,
            metadata=metadata or {},
        )

        # Save profile
        self.save_profile(profile)

        return profile

    def save_profile(self, profile: VoiceProfile) -> None:
        """
        Save voice profile to disk.

        Args:
            profile: Voice profile to save
        """
        profile.updated_at = datetime.now().isoformat()
        profile_path = self.profile_dir / f"{profile.name}.json"

        with open(profile_path, "w") as f:
            json.dump(asdict(profile), f, indent=2)

    def load_profile(self, name: str) -> VoiceProfile:
        """
        Load voice profile from disk.

        Args:
            name: Profile name

        Returns:
            Loaded voice profile

        Raises:
            FileNotFoundError: If profile doesn't exist
        """
        profile_path = self.profile_dir / f"{name}.json"

        if not profile_path.exists():
            raise FileNotFoundError(f"Profile '{name}' not found")

        with open(profile_path, "r") as f:
            data = json.load(f)

        return VoiceProfile(**data)

    def list_profiles(self) -> List[str]:
        """
        List all available voice profiles.

        Returns:
            List of profile names
        """
        profiles = []
        for file in self.profile_dir.glob("*.json"):
            profiles.append(file.stem)
        return sorted(profiles)

    def delete_profile(self, name: str) -> bool:
        """
        Delete a voice profile.

        Args:
            name: Profile name

        Returns:
            True if profile was deleted

        Raises:
            FileNotFoundError: If profile doesn't exist
        """
        profile_path = self.profile_dir / f"{name}.json"

        if not profile_path.exists():
            raise FileNotFoundError(f"Profile '{name}' not found")

        profile_path.unlink()
        return True

    def update_profile(
        self,
        name: str,
        description: Optional[str] = None,
        sample_paths: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VoiceProfile:
        """
        Update an existing voice profile.

        Args:
            name: Profile name
            description: New description (optional)
            sample_paths: New sample paths (optional)
            metadata: New metadata (optional)

        Returns:
            Updated voice profile

        Raises:
            FileNotFoundError: If profile doesn't exist
            ValueError: If new samples are invalid
        """
        # Load existing profile
        profile = self.load_profile(name)

        # Update fields
        if description is not None:
            profile.description = description

        if sample_paths is not None:
            self.validate_audio_samples(sample_paths)
            profile.sample_paths = sample_paths

        if metadata is not None:
            profile.metadata.update(metadata)

        # Save updated profile
        self.save_profile(profile)

        return profile

    def get_profile_info(self, name: str) -> Dict[str, Any]:
        """
        Get voice profile information.

        Args:
            name: Profile name

        Returns:
            Profile information dictionary

        Raises:
            FileNotFoundError: If profile doesn't exist
        """
        profile = self.load_profile(name)
        return {
            "name": profile.name,
            "description": profile.description,
            "num_samples": len(profile.sample_paths),
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "metadata": profile.metadata,
        }

