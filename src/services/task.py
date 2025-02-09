from ..models.task import Task
from ..repositories.task import TaskRepository
from ..services.user import UserService
from bson.objectid import ObjectId

class TaskService:
    def __init__(self, task_repository: TaskRepository, user_service: UserService):
        self.task_repository = task_repository
        self.user_service = user_service

    def create_task(self, title: str, description: str, user_id: str) -> dict:
        if not title or title.strip() == "":
            raise ValueError("Title cannot be empty")
        
        # Verify if user exists
        self.user_service.get_user_by_id(user_id)
        
        task = Task(title=title, description=description, user_id=user_id)
        return self.task_repository.create(task)

    def get_task(self, task_id: str, user_id: str) -> dict | None:
        if not ObjectId.is_valid(task_id):
            raise ValueError("Invalid task ID format")

        task = self.task_repository.find_by_id(task_id)
        if task and task.user_id != user_id:
            raise ValueError("Unauthorized access to task")
        return task

    def update_task(self, task_id: str, title: str | None = None, description: str | None = None) -> None:
        if not ObjectId.is_valid(task_id):
            raise ValueError("Invalid task ID format")

        existing_task = self.task_repository.find_by_id(task_id)
        if existing_task is None:
            raise ValueError("Task not found")

        updated_title = title if title is not None else existing_task.title
        updated_description = description if description is not None else existing_task.description

        if updated_title.strip() == "":
            raise ValueError("Title cannot be empty")

        task = Task(title=updated_title, description=updated_description, user_id=existing_task.user_id)
        self.task_repository.update(task_id, task)

    def delete_task(self, task_id: str) -> None:
        if not ObjectId.is_valid(task_id):
            raise ValueError("Invalid task ID format")

        existing_task = self.task_repository.find_by_id(task_id)
        if existing_task is None:
            raise ValueError("Task not found")

        self.task_repository.delete(task_id)

    def get_all_tasks(self) -> list[Task]:
        return self.task_repository.find_all()

    def get_user_tasks(self, user_id: str) -> list[Task]:
        return self.task_repository.find_by_user_id(user_id)
