from typing import List

from fastapi import APIRouter, Depends

import schemas
from dependencies import get_service_mesh
from service_mesh import ServiceMesh
from services import MeetingService

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/", response_model=schemas.Meeting, status_code=201)
async def create_meeting(meeting: schemas.MeetingCreate, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Create a new meeting with attendees.
    """
    return mesh.get_service(MeetingService).create_meeting(meeting)


@router.get("/", response_model=List[schemas.Meeting])
async def list_meetings(mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    List all meetings.
    """
    return mesh.get_service(MeetingService).list_meetings()


@router.get("/{meeting_id}", response_model=schemas.MeetingWithDetails)
async def get_meeting(meeting_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Get a specific meeting with all details (attendees, notes, tasks).
    """
    return mesh.get_service(MeetingService).get_meeting(meeting_id)


@router.put("/{meeting_id}", response_model=schemas.Meeting)
async def update_meeting(
        meeting_id: int,
        meeting: schemas.MeetingUpdate,
        mesh: ServiceMesh = Depends(get_service_mesh),
):
    """
    Update a meeting.
    """
    return mesh.get_service(MeetingService).update_meeting(meeting_id, meeting)


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Delete a meeting.
    """
    mesh.get_service(MeetingService).delete_meeting(meeting_id)
    return None