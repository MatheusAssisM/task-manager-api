from ..models.task import Task
from ..repositories.task import TaskRepository
from bson.objectid import ObjectId
from bson.errors import InvalidId

class TaskService:
    def __init__(self, task_repository):
        self.task_repository = task_repository

    def create_task(self, title: str, description: str) -> str:
        task = Task(title=title, description=description)
        return self.task_repository.create(task)

    def get_task(self, task_id):
        if not ObjectId.is_valid(task_id):
            raise ValueError("Invalid task ID format")
        
        return self.task_repository.find_by_id(task_id)

    def update_task(self, task_id: str, title: str, description: str) -> None:
        task = Task(title=title, description=description)
        self.task_repository.update(task_id, task)

    def delete_task(self, task_id: str) -> None:
        self.task_repository.delete(task_id)

    def get_all_tasks(self) -> list[Task]:
        return self.task_repository.find_all()
