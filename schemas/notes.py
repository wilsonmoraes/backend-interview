from datetime import datetime

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    content: str = Field(..., description="Note content.", examples=["Discussion about the roadmap."])


class NoteCreate(NoteBase):
    meeting_id: int = Field(..., description="ID of the meeting associated with the note.", examples=[1])


class Note(NoteBase):
    id: int = Field(..., description="Note identifier.", examples=[10])
    meeting_id: int = Field(..., description="ID of the meeting associated with the note.", examples=[1])
    created_at: datetime = Field(..., description="Note creation time.", examples=["2024-01-15T10:00:00Z"])

    class Config:
        from_attributes = True