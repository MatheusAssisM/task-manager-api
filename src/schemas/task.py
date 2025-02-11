from pydantic import BaseModel, Field
from typing import Optional


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)


class TaskStatusUpdate(BaseModel):
    completed: bool


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    user_id: str
    completed: bool


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]


class TaskCreateResponse(BaseModel):
    message: str = "Task created successfully"
    id: str


class TaskUpdateResponse(BaseModel):
    message: str = "Task updated successfully"


class TaskDeleteResponse(BaseModel):
    message: str = "Task deleted successfully"


class TaskStatusUpdateResponse(BaseModel):
    message: str = "Task status updated successfully"
