"""
Voice synthesis and cloning API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import os
import time

from src.api.schemas import (
    VoiceSynthesizeRequest,
    VoiceSynthesizeResponse,
    VoiceProfileCreateRequest,
    VoiceProfileResponse,
    VoiceProfileListResponse,
    ErrorResponse
)
from src.api.dependencies import get_voice_synthesizer, get_voice_cloner
from src.models.voice_synthesis import VoiceSynthesizer
from src.models.voice_cloning import VoiceCloner


router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


@router.post(
    "/synthesize",
    response_model=VoiceSynthesizeResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def synthesize_voice(request: VoiceSynthesizeRequest) -> VoiceSynthesizeResponse:
    """
    Synthesize speech from text using specified TTS backend.

    Args:
        request: Voice synthesis request with text and parameters

    Returns:
        VoiceSynthesizeResponse with audio file path and metadata

    Raises:
        HTTPException: If synthesis fails
    """
    try:
        # Get synthesizer instance
        synthesizer = get_voice_synthesizer(
            backend=request.backend,
            device=request.device
        )

        # Synthesize speech
        start_time = time.time()
        audio_path = synthesizer.synthesize(
            text=request.text,
            speaker_wav=request.speaker_wav
        )
        duration = time.time() - start_time

        # Get audio duration (approximate based on text length)
        # In production, you'd want to read the actual audio file duration
        estimated_duration = len(request.text.split()) * 0.5  # ~0.5s per word

        return VoiceSynthesizeResponse(
            audio_path=audio_path,
            duration=estimated_duration,
            backend=request.backend,
            text_length=len(request.text)
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")


@router.post(
    "/profiles",
    response_model=VoiceProfileResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def create_voice_profile(request: VoiceProfileCreateRequest) -> VoiceProfileResponse:
    """
    Create a new voice profile from audio samples.

    Args:
        request: Voice profile creation request with samples and metadata

    Returns:
        VoiceProfileResponse with profile information

    Raises:
        HTTPException: If profile creation fails
    """
    try:
        # Get voice cloner instance
        cloner = get_voice_cloner()

        # Create profile
        profile = cloner.create_profile(
            name=request.name,
            sample_paths=request.sample_paths,
            description=request.description,
            metadata=request.metadata
        )

        # Save profile
        cloner.save_profile(profile)

        return VoiceProfileResponse(
            name=profile.name,
            description=profile.description,
            sample_count=len(profile.sample_paths),
            created_at=profile.created_at,
            metadata=profile.metadata
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile creation failed: {str(e)}")


@router.get(
    "/profiles",
    response_model=VoiceProfileListResponse,
    responses={500: {"model": ErrorResponse}}
)
async def list_voice_profiles() -> VoiceProfileListResponse:
    """
    List all available voice profiles.

    Returns:
        VoiceProfileListResponse with list of profile names

    Raises:
        HTTPException: If listing fails
    """
    try:
        cloner = get_voice_cloner()
        profiles = cloner.list_profiles()

        return VoiceProfileListResponse(
            profiles=profiles,
            count=len(profiles)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list profiles: {str(e)}")


@router.get(
    "/profiles/{name}",
    response_model=VoiceProfileResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_voice_profile(name: str) -> VoiceProfileResponse:
    """
    Get information about a specific voice profile.

    Args:
        name: Profile name

    Returns:
        VoiceProfileResponse with profile information

    Raises:
        HTTPException: If profile not found or retrieval fails
    """
    try:
        cloner = get_voice_cloner()
        profile_info = cloner.get_profile_info(name)

        return VoiceProfileResponse(
            name=profile_info["name"],
            description=profile_info.get("description"),
            sample_count=profile_info["sample_count"],
            created_at=profile_info["created_at"],
            metadata=profile_info.get("metadata")
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Profile '{name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


@router.delete(
    "/profiles/{name}",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def delete_voice_profile(name: str) -> dict:
    """
    Delete a voice profile.

    Args:
        name: Profile name

    Returns:
        Success message

    Raises:
        HTTPException: If profile not found or deletion fails
    """
    try:
        cloner = get_voice_cloner()
        success = cloner.delete_profile(name)

        if not success:
            raise HTTPException(status_code=404, detail=f"Profile '{name}' not found")

        return {"message": f"Profile '{name}' deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete profile: {str(e)}")
