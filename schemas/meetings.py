from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from schemas.notes import Note
from schemas.tasks import Task
from schemas.users import User


class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_time: datetime


class MeetingCreate(MeetingBase):
    attendee_ids: List[int] = []


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    attendee_ids: Optional[List[int]] = None


class Meeting(MeetingBase):
    id: int
    created_at: datetime
    attendees: List[User] = []

    class Config:
        from_attributes = True


class MeetingWithDetails(Meeting):
    notes: List[Note] = []
    tasks: List[Task] = []

    class Config:
        from_attributes = True