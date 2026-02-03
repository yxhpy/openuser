"""
Scheduler monitoring API endpoints.

This module provides REST API endpoints for:
- Task statistics and metrics
- Task history and logs
- Queue status
- Performance monitoring
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.auth import get_current_user
from src.models.task import TaskStatus, TaskType
from src.models.user import User
from src.scheduler.monitor import TaskMonitor, get_task_monitor

router = APIRouter(prefix="/api/v1/scheduler/monitor", tags=["scheduler-monitor"])


# Response models
class TaskStatsResponse(BaseModel):
    """Task statistics response."""

    total: int = Field(..., description="Total number of tasks")
    by_status: Dict[str, int] = Field(..., description="Task count by status")
    by_type: Dict[str, int] = Field(..., description="Task count by type")
    success_rate: float = Field(..., description="Success rate percentage")


class TaskHistoryItem(BaseModel):
    """Task history item."""

    id: int
    name: str
    task_type: str
    status: str
    created_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    duration: Optional[float]
    error_message: Optional[str]


class TaskHistoryResponse(BaseModel):
    """Task history response."""

    tasks: List[TaskHistoryItem]
    total: int
    limit: int
    offset: int


class FailureItem(BaseModel):
    """Failed task item."""

    id: int
    name: str
    task_type: str
    error_message: Optional[str]
    completed_at: Optional[str]


class RecentFailuresResponse(BaseModel):
    """Recent failures response."""

    failures: List[FailureItem]
    total: int


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response."""

    total_tasks: int
    avg_duration_seconds: float
    success_rate: float
    tasks_per_day: float


class QueueStatusResponse(BaseModel):
    """Queue status response."""

    pending: int
    running: int
    pending_by_type: Dict[str, int]


@router.get("/stats", response_model=TaskStatsResponse)
async def get_task_statistics(
    current_user: User = Depends(get_current_user),
    monitor: TaskMonitor = Depends(get_task_monitor),
) -> TaskStatsResponse:
    """
    Get task statistics for the current user.

    Returns task counts by status and type, plus success rate.
    """
    try:
        stats = monitor.get_task_stats(user_id=current_user.id)
        return TaskStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task statistics: {str(e)}")


@router.get("/history", response_model=TaskHistoryResponse)
async def get_task_history(
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    monitor: TaskMonitor = Depends(get_task_monitor),
) -> TaskHistoryResponse:
    """
    Get task execution history for the current user.

    Supports filtering by task type and status, with pagination.
    """
    try:
        # Parse filters
        task_type_enum = TaskType(task_type) if task_type else None
        status_enum = TaskStatus(status) if status else None

        # Get history
        history = monitor.get_task_history(
            user_id=current_user.id,
            task_type=task_type_enum,
            status=status_enum,
            limit=limit,
            offset=offset,
        )

        return TaskHistoryResponse(
            tasks=[TaskHistoryItem(**item) for item in history],
            total=len(history),
            limit=limit,
            offset=offset,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid filter value: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task history: {str(e)}")


@router.get("/failures", response_model=RecentFailuresResponse)
async def get_recent_failures(
    hours: int = Query(24, ge=1, le=168, description="Look back hours"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    monitor: TaskMonitor = Depends(get_task_monitor),
) -> RecentFailuresResponse:
    """
    Get recent failed tasks for the current user.

    Returns tasks that failed within the specified time window.
    """
    try:
        failures = monitor.get_recent_failures(user_id=current_user.id, hours=hours, limit=limit)

        return RecentFailuresResponse(
            failures=[FailureItem(**item) for item in failures], total=len(failures)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent failures: {str(e)}")


@router.get("/performance", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    monitor: TaskMonitor = Depends(get_task_monitor),
) -> PerformanceMetricsResponse:
    """
    Get performance metrics for the current user.

    Returns average duration, success rate, and tasks per day.
    """
    try:
        metrics = monitor.get_performance_metrics(user_id=current_user.id, days=days)
        return PerformanceMetricsResponse(**metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@router.get("/queue", response_model=QueueStatusResponse)
async def get_queue_status(
    current_user: User = Depends(get_current_user), monitor: TaskMonitor = Depends(get_task_monitor)
) -> QueueStatusResponse:
    """
    Get current queue status.

    Returns counts of pending and running tasks.
    """
    try:
        status = monitor.get_queue_status()
        return QueueStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get queue status: {str(e)}")
