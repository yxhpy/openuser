"""
API request and response schemas using Pydantic.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, EmailStr


class VoiceSynthesizeRequest(BaseModel):
    """Request schema for voice synthesis."""

    text: str = Field(..., min_length=1, max_length=10000, description="Text to synthesize")
    backend: str = Field(default="coqui", description="TTS backend (coqui, pyttsx3, gtts)")
    speaker_wav: Optional[str] = Field(default=None, description="Path to speaker audio for voice cloning")
    device: str = Field(default="cpu", description="Device to use (cpu, cuda)")

    @field_validator("backend")
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate TTS backend."""
        allowed = ["coqui", "pyttsx3", "gtts"]
        if v not in allowed:
            raise ValueError(f"Backend must be one of {allowed}")
        return v

    @field_validator("device")
    @classmethod
    def validate_device(cls, v: str) -> str:
        """Validate device."""
        allowed = ["cpu", "cuda"]
        if v not in allowed:
            raise ValueError(f"Device must be one of {allowed}")
        return v


class VoiceSynthesizeResponse(BaseModel):
    """Response schema for voice synthesis."""

    audio_path: str = Field(..., description="Path to generated audio file")
    duration: float = Field(..., description="Audio duration in seconds")
    backend: str = Field(..., description="TTS backend used")
    text_length: int = Field(..., description="Length of input text")


class VoiceProfileCreateRequest(BaseModel):
    """Request schema for creating voice profile."""

    name: str = Field(..., min_length=1, max_length=100, description="Profile name")
    sample_paths: List[str] = Field(..., min_length=1, description="Paths to audio samples")
    description: Optional[str] = Field(default=None, description="Profile description")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class VoiceProfileResponse(BaseModel):
    """Response schema for voice profile."""

    name: str = Field(..., description="Profile name")
    description: Optional[str] = Field(default=None, description="Profile description")
    sample_count: int = Field(..., description="Number of audio samples")
    created_at: str = Field(..., description="Creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class VoiceProfileListResponse(BaseModel):
    """Response schema for listing voice profiles."""

    profiles: List[str] = Field(..., description="List of profile names")
    count: int = Field(..., description="Total number of profiles")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")


# Authentication Schemas

class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLoginRequest(BaseModel):
    """Request schema for user login."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenRefreshRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(..., description="JWT refresh token")


class UserResponse(BaseModel):
    """Response schema for user information."""

    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    is_active: bool = Field(..., description="Whether user is active")
    is_superuser: bool = Field(..., description="Whether user is superuser")
    created_at: str = Field(..., description="Account creation timestamp")
