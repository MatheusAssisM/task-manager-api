from bson.objectid import ObjectId
from ..models.task import Task

class TaskRepository:
    def __init__(self, collection):
        self.collection = collection

    def create(self, task: Task) -> str:
        result = self.collection.insert_one(task.to_dict())
        return str(result.inserted_id)

    def find_by_id(self, task_id: str) -> Task:
        task_data = self.collection.find_one({'_id': ObjectId(task_id)})
        return Task.from_dict(task_data) if task_data else None

    def update(self, task_id: str, task: Task) -> None:
        self.collection.update_one(
            {'_id': ObjectId(task_id)},
            {'$set': task.to_dict()}
        )

    def delete(self, task_id: str) -> None:
        self.collection.delete_one({'_id': ObjectId(task_id)})

    def find_all(self) -> list[Task]:
        tasks_data = self.collection.find({})
        return [Task.from_dict(task_data) for task_data in tasks_data]