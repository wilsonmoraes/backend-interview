from typing import List, Optional

from fastapi import APIRouter, Depends, Query

import schemas
from dependencies import get_service_mesh
from service_mesh import ServiceMesh
from services import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=schemas.Task, status_code=201)
async def create_task(task: schemas.TaskCreate, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Create a new task that is due at a specific meeting.
    """
    return mesh.get_service(TaskService).create_task(task)


@router.get("/", response_model=List[schemas.Task])
async def list_tasks(
        meeting_id: Optional[int] = Query(None),
        status: Optional[str] = Query(None),
        mesh: ServiceMesh = Depends(get_service_mesh),
):
    """
    List all tasks, optionally filtered by meeting_id or status.
    """
    return mesh.get_service(TaskService).list_tasks(meeting_id=meeting_id, status_filter=status)


@router.get("/{task_id}", response_model=schemas.Task)
async def get_task(task_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Get a specific task by ID.
    """
    return mesh.get_service(TaskService).get_task(task_id)


@router.put("/{task_id}", response_model=schemas.Task)
async def update_task(
        task_id: int,
        task: schemas.TaskUpdate,
        mesh: ServiceMesh = Depends(get_service_mesh),
):
    """
    Update a task (e.g., change status, reassign to different meeting).
    """
    return mesh.get_service(TaskService).update_task(task_id, task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Delete a task.
    """
    mesh.get_service(TaskService).delete_task(task_id)
    return None