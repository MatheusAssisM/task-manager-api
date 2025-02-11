class Metrics:
    def __init__(
        self, total_users=0, total_tasks=0, completed_tasks=0, active_tasks=0, id=None
    ):
        self.id = str(id) if id else None
        self.total_users = total_users
        self.total_tasks = total_tasks
        self.completed_tasks = completed_tasks
        self.active_tasks = active_tasks

    def to_dict(self):
        return {
            "total_users": self.total_users,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "active_tasks": self.active_tasks,
        }

    @staticmethod
    def from_dict(data):
        return Metrics(
            id=str(data.get("_id")) if data.get("_id") else None,
            total_users=data.get("total_users", 0),
            total_tasks=data.get("total_tasks", 0),
            completed_tasks=data.get("completed_tasks", 0),
            active_tasks=data.get("active_tasks", 0),
        )
