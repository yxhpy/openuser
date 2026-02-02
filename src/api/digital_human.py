"""
Digital Human API endpoints.

This module provides REST API endpoints for creating and managing digital humans,
and generating videos using the digital human video generation pipeline.
"""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from src.models.base import DatabaseManager
from src.models.digital_human import DigitalHuman
from src.models.video_generator import VideoGenerator, GenerationMode
from src.api.auth import get_current_user
from src.api.schemas import (
    DigitalHumanCreateRequest,
    DigitalHumanResponse,
    DigitalHumanListResponse,
    VideoGenerateRequest,
    VideoGenerateResponse,
    ErrorResponse,
)


router = APIRouter(prefix="/api/v1/digital-human", tags=["digital-human"])


def get_db_session():
    """Get database session dependency."""
    db_manager = DatabaseManager(
        database_url="sqlite:///./test.db",  # TODO: Load from config
        echo=False
    )
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def get_video_generator():
    """Get video generator dependency."""
    return VideoGenerator(
        device="cpu",  # TODO: Load from config
        mode=GenerationMode.ENHANCED_TALKING_HEAD
    )


@router.post(
    "/create",
    response_model=DigitalHumanResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    summary="Create a new digital human",
    description="Create a new digital human with image and voice profile"
)
async def create_digital_human(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    image: UploadFile = File(...),
    voice_model_path: Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Create a new digital human.

    Args:
        name: Name of the digital human
        description: Optional description
        image: Image file for the digital human
        voice_model_path: Optional path to voice model
        current_user: Current authenticated user
        db: Database session

    Returns:
        DigitalHumanResponse with created digital human details
    """
    # Validate image file
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save image file
    upload_dir = Path("uploads/digital_humans")
    upload_dir.mkdir(parents=True, exist_ok=True)

    image_filename = f"{current_user.id}_{name}_{image.filename}"
    image_path = upload_dir / image_filename

    with open(image_path, "wb") as f:
        content = await image.read()
        f.write(content)

    # Create digital human in database
    digital_human = DigitalHuman(
        user_id=current_user.id,
        name=name,
        description=description,
        image_path=str(image_path),
        voice_model_path=voice_model_path,
        is_active=True
    )

    db.add(digital_human)
    db.commit()
    db.refresh(digital_human)

    return DigitalHumanResponse(
        id=digital_human.id,
        user_id=digital_human.user_id,
        name=digital_human.name,
        description=digital_human.description,
        image_path=digital_human.image_path,
        voice_model_path=digital_human.voice_model_path,
        video_path=digital_human.video_path,
        is_active=digital_human.is_active,
        created_at=digital_human.created_at,
        updated_at=digital_human.updated_at
    )


@router.post(
    "/generate",
    response_model=VideoGenerateResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Generate video from digital human",
    description="Generate a video using the digital human with text or audio input"
)
async def generate_video(
    digital_human_id: int = Form(...),
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    mode: str = Form("enhanced_talking_head"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    video_gen: VideoGenerator = Depends(get_video_generator)
):
    """
    Generate a video from a digital human.

    Args:
        digital_human_id: ID of the digital human
        text: Text to synthesize (for text-to-video)
        audio: Audio file (for audio-to-video)
        mode: Generation mode (lipsync, talking_head, enhanced_lipsync, enhanced_talking_head)
        current_user: Current authenticated user
        db: Database session
        video_gen: Video generator instance

    Returns:
        VideoGenerateResponse with generated video path
    """
    # Validate input
    if not text and not audio:
        raise HTTPException(status_code=400, detail="Either text or audio must be provided")

    if text and audio:
        raise HTTPException(status_code=400, detail="Provide either text or audio, not both")

    # Get digital human
    digital_human = db.query(DigitalHuman).filter(
        DigitalHuman.id == digital_human_id,
        DigitalHuman.user_id == current_user.id
    ).first()

    if not digital_human:
        raise HTTPException(status_code=404, detail="Digital human not found")

    # Validate mode
    try:
        generation_mode = GenerationMode[mode.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Must be one of: {', '.join([m.name.lower() for m in GenerationMode])}"
        )

    # Update video generator mode
    video_gen.mode = generation_mode

    # Generate output path
    output_dir = Path("outputs/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{digital_human.id}_{digital_human.name}_{mode}.mp4"

    try:
        if text:
            # Text-to-video generation
            video_path = video_gen.generate_from_text(
                text=text,
                image_path=digital_human.image_path,
                output_path=str(output_path),
                speaker_wav=digital_human.voice_model_path
            )
        else:
            # Audio-to-video generation
            # Save uploaded audio file
            audio_dir = Path("uploads/audio")
            audio_dir.mkdir(parents=True, exist_ok=True)
            audio_path = audio_dir / f"{current_user.id}_{audio.filename}"

            with open(audio_path, "wb") as f:
                content = await audio.read()
                f.write(content)

            video_path = video_gen.generate_from_audio(
                image_path=digital_human.image_path,
                audio_path=str(audio_path),
                output_path=str(output_path)
            )

        # Update digital human with video path
        digital_human.video_path = video_path
        db.commit()

        return VideoGenerateResponse(
            video_path=video_path,
            digital_human_id=digital_human.id,
            mode=mode,
            message="Video generated successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@router.get(
    "/list",
    response_model=DigitalHumanListResponse,
    responses={401: {"model": ErrorResponse}},
    summary="List all digital humans",
    description="Get a list of all digital humans for the current user"
)
async def list_digital_humans(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    List all digital humans for the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        DigitalHumanListResponse with list of digital humans
    """
    digital_humans = db.query(DigitalHuman).filter(
        DigitalHuman.user_id == current_user.id
    ).all()

    return DigitalHumanListResponse(
        digital_humans=[
            DigitalHumanResponse(
                id=dh.id,
                user_id=dh.user_id,
                name=dh.name,
                description=dh.description,
                image_path=dh.image_path,
                voice_model_path=dh.voice_model_path,
                video_path=dh.video_path,
                is_active=dh.is_active,
                created_at=dh.created_at,
                updated_at=dh.updated_at
            )
            for dh in digital_humans
        ],
        total=len(digital_humans)
    )


@router.get(
    "/{digital_human_id}",
    response_model=DigitalHumanResponse,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Get digital human details",
    description="Get details of a specific digital human"
)
async def get_digital_human(
    digital_human_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Get details of a specific digital human.

    Args:
        digital_human_id: ID of the digital human
        current_user: Current authenticated user
        db: Database session

    Returns:
        DigitalHumanResponse with digital human details
    """
    digital_human = db.query(DigitalHuman).filter(
        DigitalHuman.id == digital_human_id,
        DigitalHuman.user_id == current_user.id
    ).first()

    if not digital_human:
        raise HTTPException(status_code=404, detail="Digital human not found")

    return DigitalHumanResponse(
        id=digital_human.id,
        user_id=digital_human.user_id,
        name=digital_human.name,
        description=digital_human.description,
        image_path=digital_human.image_path,
        voice_model_path=digital_human.voice_model_path,
        video_path=digital_human.video_path,
        is_active=digital_human.is_active,
        created_at=digital_human.created_at,
        updated_at=digital_human.updated_at
    )


@router.delete(
    "/{digital_human_id}",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Delete digital human",
    description="Delete a specific digital human"
)
async def delete_digital_human(
    digital_human_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Delete a specific digital human.

    Args:
        digital_human_id: ID of the digital human
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    digital_human = db.query(DigitalHuman).filter(
        DigitalHuman.id == digital_human_id,
        DigitalHuman.user_id == current_user.id
    ).first()

    if not digital_human:
        raise HTTPException(status_code=404, detail="Digital human not found")

    # Delete associated files
    if digital_human.image_path and Path(digital_human.image_path).exists():
        Path(digital_human.image_path).unlink()

    if digital_human.video_path and Path(digital_human.video_path).exists():
        Path(digital_human.video_path).unlink()

    db.delete(digital_human)
    db.commit()

    return {"message": "Digital human deleted successfully"}
