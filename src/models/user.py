class User:
    def __init__(self, username, email, password, id=None):
        self.id = str(id) if id else None
        self.username = username
        self.email = email
        self.password = password  # Note: In production, this should be hashed

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }

    @staticmethod
    def from_dict(data):
        return User(
            id=str(data.get("_id")),
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password")
        )