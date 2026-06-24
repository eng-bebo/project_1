from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field
Priority = Literal["low", "medium", "high"]

class TaskCreate(BaseModel):

    title: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Short name for the task.",
        examples=["Buy groceries"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional longer notes about the task.",
        examples=["Milk, eggs, and bread from the corner store."],
    )
    priority: Priority = Field(
        default="medium",
        description="Task urgency: 'low', 'medium', or 'high'.",
        examples=["high"],
    )


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):

    id: int
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class TaskListResponse(BaseModel):
    total: int = Field(..., description="Total number of tasks matching the query.")
    tasks: list[TaskResponse]
