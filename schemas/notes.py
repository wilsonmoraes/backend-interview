from datetime import datetime

from pydantic import BaseModel


class NoteBase(BaseModel):
    content: str


class NoteCreate(NoteBase):
    meeting_id: int


class Note(NoteBase):
    id: int
    meeting_id: int
    created_at: datetime

    class Config:
        from_attributes = True