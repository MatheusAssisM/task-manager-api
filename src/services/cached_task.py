import json
from redis import StrictRedis
from ..models.task import Task
from .task import TaskService


class CachedTaskService:
    def __init__(self, task_service: TaskService, redis_client: StrictRedis):
        self.task_service = task_service
        self.redis_client = redis_client
        self.cache_prefix = "task:"
        self.user_tasks_prefix = "user_tasks:"
        self.cache_ttl = 3600  # 1 hour

    def _get_task_key(self, task_id: str) -> str:
        return f"{self.cache_prefix}{task_id}"

    def _get_user_tasks_key(self, user_id: str) -> str:
        return f"{self.user_tasks_prefix}{user_id}"

    def _cache_task(self, task: Task) -> None:
        if task and task.id:
            self.redis_client.setex(
                self._get_task_key(task.id),
                self.cache_ttl,
                json.dumps({"id": task.id, **task.to_dict()})
            )

    def _invalidate_user_tasks_cache(self, user_id: str) -> None:
        self.redis_client.delete(self._get_user_tasks_key(user_id))

    def create_task(self, title: str, description: str, user_id: str) -> str:
        task_id = self.task_service.create_task(title, description, user_id)
        self._invalidate_user_tasks_cache(user_id)
        return task_id

    def get_task(self, task_id: str, user_id: str) -> Task:
        # Try to get from cache first
        cached_task = self.redis_client.get(self._get_task_key(task_id))
        if cached_task:
            task_data = json.loads(cached_task)
            task = Task(
                id=task_data.get("id"),
                title=task_data.get("title"),
                description=task_data.get("description"),
                user_id=task_data.get("user_id"),
                completed=task_data.get("completed", False)
            )
            # Verify task belongs to user
            if task.user_id != user_id:
                raise ValueError("Unauthorized access to task")
            return task

        # If not in cache, get from service and cache it
        task = self.task_service.get_task(task_id, user_id)
        if task:
            self._cache_task(task)
        return task

    def update_task(self, task_id: str, title: str | None, description: str | None, user_id: str) -> None:
        self.task_service.update_task(task_id, title, description, user_id)
        # Invalidate caches
        self.redis_client.delete(self._get_task_key(task_id))
        self._invalidate_user_tasks_cache(user_id)

    def update_task_status(self, task_id: str, completed: bool, user_id: str) -> None:
        self.task_service.update_task_status(task_id, completed, user_id)
        # Invalidate caches
        self.redis_client.delete(self._get_task_key(task_id))
        self._invalidate_user_tasks_cache(user_id)

    def delete_task(self, task_id: str, user_id: str) -> None:
        self.task_service.delete_task(task_id, user_id)
        # Invalidate caches
        self.redis_client.delete(self._get_task_key(task_id))
        self._invalidate_user_tasks_cache(user_id)

    def get_user_tasks(self, user_id: str) -> list[Task]:
        # Try to get from cache first
        cached_tasks = self.redis_client.get(self._get_user_tasks_key(user_id))
        if cached_tasks:
            tasks_data = json.loads(cached_tasks)
            return [Task(
                id=task_data.get("id"),
                title=task_data.get("title"),
                description=task_data.get("description"),
                user_id=task_data.get("user_id"),
                completed=task_data.get("completed", False)
            ) for task_data in tasks_data]

        # If not in cache, get from service and cache it
        tasks = self.task_service.get_user_tasks(user_id)
        if tasks:
            tasks_data = [{"id": task.id, **task.to_dict()} for task in tasks]
            self.redis_client.setex(
                self._get_user_tasks_key(user_id),
                self.cache_ttl,
                json.dumps(tasks_data)
            )
        return tasks