from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from service_mesh import service_class, service_tool


class BaseService:
    def __init__(self, mesh: "ServiceMesh", db: Session, user: Optional[models.User]) -> None:
        self.mesh = mesh
        self.db = db
        self.user = user

    def _require_user(self) -> models.User:
        if not self.user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        return self.user


@service_class("users")
class UserService(BaseService):
    @service_tool()
    def create_user(self, user_in: schemas.UserCreate) -> models.User:
        if self.user:
            owner_id = self.user.id
            user = models.User(name=user_in.name, email=user_in.email, owner_id=owner_id)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user

        user = models.User(name=user_in.name, email=user_in.email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        user.owner_id = user.id
        self.db.commit()
        self.db.refresh(user)
        return user

    @service_tool()
    def list_users(self) -> List[models.User]:
        current_user = self._require_user()
        return (
            self.db.query(models.User)
            .filter(models.User.owner_id == current_user.id)
            .order_by(models.User.id)
            .all()
        )

    @service_tool()
    def get_user(self, user_id: int) -> models.User:
        current_user = self._require_user()
        user = (
            self.db.query(models.User)
            .filter(models.User.id == user_id, models.User.owner_id == current_user.id)
            .first()
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def get_users_by_ids(self, user_ids: List[int]) -> List[models.User]:
        current_user = self._require_user()
        if not user_ids:
            return []
        return (
            self.db.query(models.User)
            .filter(models.User.owner_id == current_user.id, models.User.id.in_(user_ids))
            .all()
        )


@service_class("meetings")
class MeetingService(BaseService):
    @service_tool()
    def create_meeting(self, meeting_in: schemas.MeetingCreate) -> models.Meeting:
        current_user = self._require_user()
        attendees = self.mesh.get_service(UserService).get_users_by_ids(meeting_in.attendee_ids)
        if len(attendees) != len(set(meeting_in.attendee_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid attendee IDs")
        meeting = models.Meeting(
            title=meeting_in.title,
            description=meeting_in.description,
            scheduled_time=meeting_in.scheduled_time,
            created_at=datetime.utcnow(),
            attendees=attendees,
            owner_id=current_user.id,
        )
        self.db.add(meeting)
        self.db.commit()
        self.db.refresh(meeting)
        return meeting

    @service_tool()
    def list_meetings(self) -> List[models.Meeting]:
        current_user = self._require_user()
        return (
            self.db.query(models.Meeting)
            .filter(models.Meeting.owner_id == current_user.id)
            .order_by(models.Meeting.id)
            .all()
        )

    @service_tool()
    def get_meeting(self, meeting_id: int) -> schemas.MeetingWithDetails:
        meeting = self.get_meeting_model(meeting_id)
        notes = self.mesh.get_service(NoteService).list_notes(meeting_id=meeting_id)
        tasks = self.mesh.get_service(TaskService).list_tasks(meeting_id=meeting_id)
        return schemas.MeetingWithDetails(
            id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            scheduled_time=meeting.scheduled_time,
            created_at=meeting.created_at,
            attendees=meeting.attendees,
            notes=notes,
            tasks=tasks,
        )

    @service_tool()
    def update_meeting(self, meeting_id: int, meeting_in: schemas.MeetingUpdate) -> models.Meeting:
        meeting = self.get_meeting_model(meeting_id)
        if meeting_in.title is not None:
            meeting.title = meeting_in.title
        if meeting_in.description is not None:
            meeting.description = meeting_in.description
        if meeting_in.scheduled_time is not None:
            meeting.scheduled_time = meeting_in.scheduled_time
        if meeting_in.attendee_ids is not None:
            attendees = self.mesh.get_service(UserService).get_users_by_ids(meeting_in.attendee_ids)
            if len(attendees) != len(set(meeting_in.attendee_ids)):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid attendee IDs")
            meeting.attendees = attendees
        self.db.commit()
        self.db.refresh(meeting)
        return meeting

    @service_tool()
    def delete_meeting(self, meeting_id: int) -> None:
        meeting = self.get_meeting_model(meeting_id)
        self.db.delete(meeting)
        self.db.commit()

    def get_meeting_model(self, meeting_id: int) -> models.Meeting:
        current_user = self._require_user()
        meeting = (
            self.db.query(models.Meeting)
            .filter(models.Meeting.id == meeting_id, models.Meeting.owner_id == current_user.id)
            .first()
        )
        if not meeting:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
        return meeting


@service_class("notes")
class NoteService(BaseService):
    @service_tool()
    def create_note(self, note_in: schemas.NoteCreate) -> models.Note:
        current_user = self._require_user()
        self.mesh.get_service(MeetingService).get_meeting_model(note_in.meeting_id)
        note = models.Note(
            content=note_in.content,
            meeting_id=note_in.meeting_id,
            created_at=datetime.utcnow(),
            owner_id=current_user.id,
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    @service_tool()
    def list_notes(self, meeting_id: Optional[int] = None) -> List[models.Note]:
        current_user = self._require_user()
        query = self.db.query(models.Note).filter(models.Note.owner_id == current_user.id)
        if meeting_id is not None:
            self.mesh.get_service(MeetingService).get_meeting_model(meeting_id)
            query = query.filter(models.Note.meeting_id == meeting_id)
        return query.order_by(models.Note.id).all()

    @service_tool()
    def get_note(self, note_id: int) -> models.Note:
        current_user = self._require_user()
        note = (
            self.db.query(models.Note)
            .filter(models.Note.id == note_id, models.Note.owner_id == current_user.id)
            .first()
        )
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        return note


@service_class("tasks")
class TaskService(BaseService):
    @service_tool()
    def create_task(self, task_in: schemas.TaskCreate) -> models.Task:
        current_user = self._require_user()
        self.mesh.get_service(MeetingService).get_meeting_model(task_in.due_meeting_id)
        task = models.Task(
            title=task_in.title,
            description=task_in.description,
            status=task_in.status,
            due_meeting_id=task_in.due_meeting_id,
            created_at=datetime.utcnow(),
            owner_id=current_user.id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    @service_tool()
    def list_tasks(self, meeting_id: Optional[int] = None, status_filter: Optional[str] = None) -> List[models.Task]:
        current_user = self._require_user()
        query = self.db.query(models.Task).filter(models.Task.owner_id == current_user.id)
        if meeting_id is not None:
            self.mesh.get_service(MeetingService).get_meeting_model(meeting_id)
            query = query.filter(models.Task.due_meeting_id == meeting_id)
        if status_filter is not None:
            query = query.filter(models.Task.status == status_filter)
        return query.order_by(models.Task.id).all()

    @service_tool()
    def get_task(self, task_id: int) -> models.Task:
        current_user = self._require_user()
        task = (
            self.db.query(models.Task)
            .filter(models.Task.id == task_id, models.Task.owner_id == current_user.id)
            .first()
        )
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    @service_tool()
    def update_task(self, task_id: int, task_in: schemas.TaskUpdate) -> models.Task:
        task = self.get_task(task_id)
        if task_in.title is not None:
            task.title = task_in.title
        if task_in.description is not None:
            task.description = task_in.description
        if task_in.status is not None:
            task.status = task_in.status
        if task_in.due_meeting_id is not None:
            self.mesh.get_service(MeetingService).get_meeting_model(task_in.due_meeting_id)
            task.due_meeting_id = task_in.due_meeting_id
        self.db.commit()
        self.db.refresh(task)
        return task

    @service_tool()
    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.db.delete(task)
        self.db.commit()