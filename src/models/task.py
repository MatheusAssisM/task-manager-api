class Task:
    def __init__(self, title, description, id=None):
        self.id = str(id) if id else None
        self.title = title
        self.description = description

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description
        }

    @staticmethod
    def from_dict(data):
        return Task(
            id=str(data.get('_id')),
            title=data.get('title'),
            description=data.get('description')
        )