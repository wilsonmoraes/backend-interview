from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    title: str = Field(..., description="Task title.", examples=["Implement feature X"])
    description: Optional[str] = Field(None, description="Task description.", examples=["Complete implementation and tests."])
    status: str = Field("pending", description="Task status (pending, completed, cancelled).", examples=["pending"])


class TaskCreate(TaskBase):
    due_meeting_id: int = Field(..., description="ID of the meeting the task is due at.", examples=[1])


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Task title.", examples=["Update documentation"])
    description: Optional[str] = Field(None, description="Task description.", examples=["Add examples to the README."])
    status: Optional[str] = Field(None, description="Task status (pending, completed, cancelled).", examples=["completed"])
    due_meeting_id: Optional[int] = Field(None, description="ID of the meeting the task is due at.", examples=[2])


class Task(TaskBase):
    id: int = Field(..., description="Task identifier.", examples=[5])
    due_meeting_id: int = Field(..., description="ID of the meeting the task is due at.", examples=[1])
    created_at: datetime = Field(..., description="Task creation time.", examples=["2024-01-15T10:00:00Z"])

    class Config:
        from_attributes = True