from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from schemas.notes import Note
from schemas.tasks import Task
from schemas.users import User


class MeetingBase(BaseModel):
    title: str = Field(..., description="Meeting title.", examples=["Sprint Planning"])
    description: Optional[str] = Field(None, description="Meeting description.", examples=["Q1 planning."])
    scheduled_time: datetime = Field(..., description="Scheduled date and time.", examples=["2024-01-15T10:00:00Z"])


class MeetingCreate(MeetingBase):
    attendee_ids: List[int] = Field(default_factory=list, description="Attendee IDs.", examples=[[1, 2]])


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Meeting title.", examples=["Sprint Review"])
    description: Optional[str] = Field(None, description="Meeting description.", examples=["Review deliveries and metrics."])
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled date and time.", examples=["2024-01-20T15:00:00Z"])
    attendee_ids: Optional[List[int]] = Field(None, description="Attendee IDs.", examples=[[2, 3]])


class Meeting(MeetingBase):
    id: int = Field(..., description="Meeting identifier.", examples=[3])
    created_at: datetime = Field(..., description="Meeting creation time.", examples=["2024-01-10T09:00:00Z"])
    attendees: List[User] = Field(default_factory=list, description="List of attendees.")

    class Config:
        from_attributes = True


class MeetingWithDetails(Meeting):
    notes: List[Note] = Field(default_factory=list, description="Notes associated with the meeting.")
    tasks: List[Task] = Field(default_factory=list, description="Tasks associated with the meeting.")

    class Config:
        from_attributes = True