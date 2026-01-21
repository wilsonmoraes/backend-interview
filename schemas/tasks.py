from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"


class TaskCreate(TaskBase):
    due_meeting_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_meeting_id: Optional[int] = None


class Task(TaskBase):
    id: int
    due_meeting_id: int
    created_at: datetime

    class Config:
        from_attributes = True