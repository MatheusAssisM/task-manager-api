from ..models.task import Task
from ..repositories.task import TaskRepository
from ..services.user import UserService
from bson.objectid import ObjectId
from ..utils.logger import setup_logger

logger = setup_logger('task_service')

class TaskService:
    def __init__(self, task_repository: TaskRepository, user_service: UserService):
        self.task_repository = task_repository
        self.user_service = user_service

    def create_task(self, title: str, description: str, user_id: str) -> dict:
        if not title or title.strip() == "":
            logger.error(f"Attempted to create task with empty title for user {user_id}")
            raise ValueError("Title cannot be empty")

        # Verify if user exists
        self.user_service.get_user_by_id(user_id)

        task = Task(title=title, description=description, user_id=user_id)
        task_id = self.task_repository.create(task)
        logger.info(f"Task created successfully: {task_id} for user {user_id}")
        return task_id

    def get_task(self, task_id: str, user_id: str) -> dict | None:
        if not ObjectId.is_valid(task_id):
            logger.error(f"Invalid task ID format: {task_id}")
            raise ValueError("Invalid task ID format")

        task = self.task_repository.find_by_id(task_id)
        if task and task.user_id != user_id:
            logger.warning(f"Unauthorized access attempt to task {task_id} by user {user_id}")
            raise ValueError("Unauthorized access to task")
        return task

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        user_id: str = None,
    ) -> None:
        if not ObjectId.is_valid(task_id):
            raise ValueError("Invalid task ID format")

        existing_task = self.task_repository.find_by_id(task_id)
        if existing_task is None:
            raise ValueError("Task not found")

        if existing_task.user_id != user_id:
            raise ValueError("Unauthorized access to task")

        updated_title = title if title is not None else existing_task.title
        updated_description = (
            description if description is not None else existing_task.description
        )

        if updated_title.strip() == "":
            raise ValueError("Title cannot be empty")

        task = Task(
            title=updated_title,
            description=updated_description,
            user_id=existing_task.user_id,
            completed=existing_task.completed  # Preserve the existing completed status
        )
        self.task_repository.update(task_id, task)

    def update_task_status(self, task_id: str, completed: bool, user_id: str) -> None:
        if not ObjectId.is_valid(task_id):
            logger.error(f"Invalid task ID format: {task_id}")
            raise ValueError("Invalid task ID format")

        existing_task = self.task_repository.find_by_id(task_id)
        if existing_task is None:
            logger.error(f"Task not found: {task_id}")
            raise ValueError("Task not found")

        if existing_task.user_id != user_id:
            logger.warning(f"Unauthorized status update attempt for task {task_id} by user {user_id}")
            raise ValueError("Unauthorized access to task")

        task = Task(
            title=existing_task.title,
            description=existing_task.description,
            user_id=existing_task.user_id,
            completed=completed
        )
        self.task_repository.update(task_id, task)
        logger.info(f"Task {task_id} completed status updated to {completed} by user {user_id}")

    def delete_task(self, task_id: str, user_id: str) -> None:
        if not ObjectId.is_valid(task_id):
            logger.error(f"Invalid task ID format: {task_id}")
            raise ValueError("Invalid task ID format")

        existing_task = self.task_repository.find_by_id(task_id)
        if existing_task is None:
            logger.error(f"Attempt to delete non-existent task: {task_id}")
            raise ValueError("Task not found")

        if existing_task.user_id != user_id:
            logger.warning(f"Unauthorized deletion attempt for task {task_id} by user {user_id}")
            raise ValueError("Unauthorized access to task")

        self.task_repository.delete(task_id)
        logger.info(f"Task {task_id} deleted successfully by user {user_id}")

    def get_all_tasks(self) -> list[Task]:
        return self.task_repository.find_all()

    def get_user_tasks(self, user_id: str) -> list[Task]:
        return self.task_repository.find_by_user_id(user_id)
