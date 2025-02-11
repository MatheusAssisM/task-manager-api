from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_users: int
    total_tasks: int
    completed_tasks: int
    active_tasks: int


class MetricsErrorResponse(BaseModel):
    error: str = "Internal server error"
