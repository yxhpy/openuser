"""
API request and response schemas using Pydantic.
"""
from datetime import datetime
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


# Digital Human Schemas

class DigitalHumanCreateRequest(BaseModel):
    """Request schema for creating a digital human."""

    name: str = Field(..., min_length=1, max_length=100, description="Digital human name")
    description: Optional[str] = Field(default=None, description="Digital human description")
    voice_model_path: Optional[str] = Field(default=None, description="Path to voice model")


class DigitalHumanResponse(BaseModel):
    """Response schema for digital human."""

    id: int = Field(..., description="Digital human ID")
    user_id: int = Field(..., description="Owner user ID")
    name: str = Field(..., description="Digital human name")
    description: Optional[str] = Field(default=None, description="Digital human description")
    image_path: Optional[str] = Field(default=None, description="Path to image file")
    voice_model_path: Optional[str] = Field(default=None, description="Path to voice model")
    video_path: Optional[str] = Field(default=None, description="Path to generated video")
    is_active: bool = Field(..., description="Whether digital human is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class DigitalHumanListResponse(BaseModel):
    """Response schema for listing digital humans."""

    digital_humans: List[DigitalHumanResponse] = Field(..., description="List of digital humans")
    total: int = Field(..., description="Total number of digital humans")


class VideoGenerateRequest(BaseModel):
    """Request schema for video generation."""

    digital_human_id: int = Field(..., description="Digital human ID")
    text: Optional[str] = Field(default=None, description="Text to synthesize (for text-to-video)")
    mode: str = Field(default="enhanced_talking_head", description="Generation mode")

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Validate generation mode."""
        allowed = ["lipsync", "talking_head", "enhanced_lipsync", "enhanced_talking_head"]
        if v not in allowed:
            raise ValueError(f"Mode must be one of {allowed}")
        return v


class VideoGenerateResponse(BaseModel):
    """Response schema for video generation."""

    video_path: str = Field(..., description="Path to generated video")
    digital_human_id: int = Field(..., description="Digital human ID")
    mode: str = Field(..., description="Generation mode used")
    message: str = Field(..., description="Success message")


# Plugin Schemas

class PluginInfo(BaseModel):
    """Plugin information schema."""

    name: str = Field(..., description="Plugin name")
    version: str = Field(..., description="Plugin version")
    dependencies: List[str] = Field(default_factory=list, description="Plugin dependencies")


class PluginListResponse(BaseModel):
    """Response schema for listing plugins."""

    plugins: List[PluginInfo] = Field(..., description="List of plugins")
    total: int = Field(..., description="Total number of plugins")


class PluginInstallRequest(BaseModel):
    """Request schema for installing a plugin."""

    name: str = Field(..., min_length=1, max_length=100, description="Plugin name to install")


class PluginInstallResponse(BaseModel):
    """Response schema for plugin installation."""

    name: str = Field(..., description="Installed plugin name")
    version: str = Field(..., description="Installed plugin version")
    message: str = Field(..., description="Success message")


class PluginReloadRequest(BaseModel):
    """Request schema for reloading a plugin."""

    name: str = Field(..., min_length=1, max_length=100, description="Plugin name to reload")


class PluginReloadResponse(BaseModel):
    """Response schema for plugin reload."""

    name: str = Field(..., description="Reloaded plugin name")
    version: str = Field(..., description="Reloaded plugin version")
    message: str = Field(..., description="Success message")


# Agent Schemas

class AgentCreateRequest(BaseModel):
    """Request schema for creating an agent."""

    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    system_prompt: str = Field(..., min_length=1, description="Agent system prompt")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")


class AgentUpdateRequest(BaseModel):
    """Request schema for updating an agent."""

    system_prompt: Optional[str] = Field(default=None, description="New system prompt")
    capabilities: Optional[List[str]] = Field(default=None, description="New capabilities")


class AgentResponse(BaseModel):
    """Response schema for agent information."""

    name: str = Field(..., description="Agent name")
    system_prompt: str = Field(..., description="Agent system prompt")
    capabilities: List[str] = Field(..., description="Agent capabilities")


class AgentListResponse(BaseModel):
    """Response schema for listing agents."""

    agents: List[AgentResponse] = Field(..., description="List of agents")
    total: int = Field(..., description="Total number of agents")

