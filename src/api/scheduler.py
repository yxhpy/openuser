"""
Scheduler API endpoints for task management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models.task import Task, TaskStatus, TaskType
from src.models.base import get_db
from src.api.auth import get_current_user
from src.api.schemas import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
    TaskListResponse,
    ErrorResponse
)

router = APIRouter(prefix="/api/v1/scheduler", tags=["scheduler"])


@router.post(
    "/create",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "Bad Request"}
    }
)
async def create_task(
    request: TaskCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new scheduled task.

    Args:
        request: Task creation request
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created task information
    """
    try:
        # Validate task type
        try:
            TaskType(request.task_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid task type: {request.task_type}"
            )

        # Create task
        task = Task(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            task_type=request.task_type,
            schedule=request.schedule,
            params=request.params,
            status=TaskStatus.PENDING.value
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            name=task.name,
            description=task.description,
            task_type=task.task_type,
            schedule=task.schedule,
            params=task.params,
            status=task.status,
            result=task.result,
            error_message=task.error_message,
            started_at=task.started_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get(
    "/list",
    response_model=TaskListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def list_tasks(
    task_status: Optional[str] = None,
    task_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all tasks for the current user.

    Args:
        task_status: Filter by task status (optional)
        task_type: Filter by task type (optional)
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of tasks
    """
    try:
        # Build query
        query = db.query(Task).filter(Task.user_id == current_user.id)

        # Apply filters
        if task_status:
            try:
                TaskStatus(task_status)
                query = query.filter(Task.status == task_status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {task_status}"
                )

        if task_type:
            try:
                TaskType(task_type)
                query = query.filter(Task.task_type == task_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid task type: {task_type}"
                )

        # Execute query
        tasks = query.order_by(Task.created_at.desc()).all()

        # Convert to response
        task_responses = [
            TaskResponse(
                id=task.id,
                user_id=task.user_id,
                name=task.name,
                description=task.description,
                task_type=task.task_type,
                schedule=task.schedule,
                params=task.params,
                status=task.status,
                result=task.result,
                error_message=task.error_message,
                started_at=task.started_at,
                completed_at=task.completed_at,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in tasks
        ]

        return TaskListResponse(
            tasks=task_responses,
            total=len(task_responses)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}"
        )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Task not found"}
    }
)
async def get_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get task details by ID.

    Args:
        task_id: Task ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Task information
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        name=task.name,
        description=task.description,
        task_type=task.task_type,
        schedule=task.schedule,
        params=task.params,
        status=task.status,
        result=task.result,
        error_message=task.error_message,
        started_at=task.started_at,
        completed_at=task.completed_at,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Task not found"}
    }
)
async def update_task(
    task_id: int,
    request: TaskUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a task.

    Args:
        task_id: Task ID
        request: Task update request
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated task information
    """
    try:
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == current_user.id
        ).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        # Update fields
        if request.name is not None:
            task.name = request.name
        if request.description is not None:
            task.description = request.description
        if request.schedule is not None:
            task.schedule = request.schedule
        if request.params is not None:
            task.params = request.params
        if request.status is not None:
            try:
                TaskStatus(request.status)
                task.status = request.status
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {request.status}"
                )

        db.commit()
        db.refresh(task)

        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            name=task.name,
            description=task.description,
            task_type=task.task_type,
            schedule=task.schedule,
            params=task.params,
            status=task.status,
            result=task.result,
            error_message=task.error_message,
            started_at=task.started_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Task not found"}
    }
)
async def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task.

    Args:
        task_id: Task ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        No content on success
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    db.delete(task)
    db.commit()

