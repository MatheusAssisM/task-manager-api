class Task:
    def __init__(self, title, description, user_id, id=None):
        self.id = str(id) if id else None
        self.title = title
        self.description = description
        self.user_id = user_id

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
        }

    @staticmethod
    def from_dict(data):
        return Task(
            id=str(data.get("_id")),
            title=data.get("title"),
            description=data.get("description"),
            user_id=data.get("user_id"),
        )
