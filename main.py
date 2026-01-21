from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

import schemas
from auth import get_current_user, get_optional_user
from database import create_tables, get_db
from service_mesh import ServiceMesh
from services import MeetingService, NoteService, TaskService, UserService

app = FastAPI(
    title="Meeting Notes API",
    description="API for managing meetings, notes, and tasks",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


def get_service_mesh(
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
) -> ServiceMesh:
    return ServiceMesh(user=current_user, db=db)


def get_optional_service_mesh(
        current_user=Depends(get_optional_user),
        db: Session = Depends(get_db),
) -> ServiceMesh:
    return ServiceMesh(user=current_user, db=db)


# User endpoints
@app.post("/users/", response_model=schemas.User, status_code=201)
async def create_user(user: schemas.UserCreate, mesh: ServiceMesh = Depends(get_optional_service_mesh)):
    """
    Create a new user.
    """
    return mesh.get_service(UserService).create_user(user)


@app.get("/users/", response_model=List[schemas.User])
async def list_users(mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    List all users.
    """
    return mesh.get_service(UserService).list_users()


@app.get("/users/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Get a specific user by ID.
    """
    return mesh.get_service(UserService).get_user(user_id)


# Meeting endpoints
@app.post("/meetings/", response_model=schemas.Meeting, status_code=201)
async def create_meeting(meeting: schemas.MeetingCreate, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Create a new meeting with attendees.
    """
    return mesh.get_service(MeetingService).create_meeting(meeting)


@app.get("/meetings/", response_model=List[schemas.Meeting])
async def list_meetings(mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    List all meetings.
    """
    return mesh.get_service(MeetingService).list_meetings()


@app.get("/meetings/{meeting_id}", response_model=schemas.MeetingWithDetails)
async def get_meeting(meeting_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Get a specific meeting with all details (attendees, notes, tasks).
    """
    return mesh.get_service(MeetingService).get_meeting(meeting_id)


@app.put("/meetings/{meeting_id}", response_model=schemas.Meeting)
async def update_meeting(
        meeting_id: int,
        meeting: schemas.MeetingUpdate,
        mesh: ServiceMesh = Depends(get_service_mesh),
):
    """
    Update a meeting.
    """
    return mesh.get_service(MeetingService).update_meeting(meeting_id, meeting)


@app.delete("/meetings/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Delete a meeting.
    """
    mesh.get_service(MeetingService).delete_meeting(meeting_id)
    return None


# Note endpoints
@app.post("/notes/", response_model=schemas.Note, status_code=201)
async def create_note(note: schemas.NoteCreate, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Create a new note for a meeting.
    """
    return mesh.get_service(NoteService).create_note(note)


@app.get("/notes/", response_model=List[schemas.Note])
async def list_notes(meeting_id: Optional[int] = Query(None), mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    List all notes, optionally filtered by meeting_id.
    """
    return mesh.get_service(NoteService).list_notes(meeting_id=meeting_id)


@app.get("/notes/{note_id}", response_model=schemas.Note)
async def get_note(note_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Get a specific note by ID.
    """
    return mesh.get_service(NoteService).get_note(note_id)


# Task endpoints
@app.post("/tasks/", response_model=schemas.Task, status_code=201)
async def create_task(task: schemas.TaskCreate, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Create a new task that is due at a specific meeting.
    """
    return mesh.get_service(TaskService).create_task(task)


@app.get("/tasks/", response_model=List[schemas.Task])
async def list_tasks(
        meeting_id: Optional[int] = Query(None),
        status: Optional[str] = Query(None),
        mesh: ServiceMesh = Depends(get_service_mesh),
):
    """
    List all tasks, optionally filtered by meeting_id or status.
    """
    return mesh.get_service(TaskService).list_tasks(meeting_id=meeting_id, status_filter=status)


@app.get("/tasks/{task_id}", response_model=schemas.Task)
async def get_task(task_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Get a specific task by ID.
    """
    return mesh.get_service(TaskService).get_task(task_id)


@app.put("/tasks/{task_id}", response_model=schemas.Task)
async def update_task(
        task_id: int,
        task: schemas.TaskUpdate,
        mesh: ServiceMesh = Depends(get_service_mesh),
):
    """
    Update a task (e.g., change status, reassign to different meeting).
    """
    return mesh.get_service(TaskService).update_task(task_id, task)


@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, mesh: ServiceMesh = Depends(get_service_mesh)):
    """
    Delete a task.
    """
    mesh.get_service(TaskService).delete_task(task_id)
    return None


@app.get("/")
async def root():
    """
    Root endpoint to verify the API is running.
    """
    return {
        "message": "Welcome to the Meeting Notes API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/users/",
            "meetings": "/meetings/",
            "notes": "/notes/",
            "tasks": "/tasks/"
        }
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
