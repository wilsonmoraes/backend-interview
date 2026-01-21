from typing import List, Optional

from fastapi import APIRouter, Depends, Query

import schemas
from dependencies import get_service_mesh
from service_mesh import ServiceMesh
from services import NoteService

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=schemas.Note, status_code=201)
async def create_note(note: schemas.NoteCreate, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Create a new note for a meeting.
    """
    return mesh.get_service(NoteService).create_note(note)


@router.get("/", response_model=List[schemas.Note])
async def list_notes(
        meeting_id: Optional[int] = Query(None),
        mesh: ServiceMesh = Depends(get_service_mesh),
):
    """
    List all notes, optionally filtered by meeting_id.
    """
    return mesh.get_service(NoteService).list_notes(meeting_id=meeting_id)


@router.get("/{note_id}", response_model=schemas.Note)
async def get_note(note_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Get a specific note by ID.
    """
    return mesh.get_service(NoteService).get_note(note_id)