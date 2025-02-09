from bson.objectid import ObjectId
from ..models.user import User


class UserRepository:
    def __init__(self, collection):
        self.collection = collection

    def create(self, user: User) -> str:
        result = self.collection.insert_one(user.to_dict())
        return str(result.inserted_id)

    def find_by_id(self, user_id: str) -> User:
        user_data = self.collection.find_one({"_id": ObjectId(user_id)})
        return User.from_dict(user_data) if user_data else None

    def find_by_email(self, email: str) -> User:
        user_data = self.collection.find_one({"email": email})
        return User.from_dict(user_data) if user_data else None

    def update(self, user: User) -> None:
        self.collection.update_one({"_id": ObjectId(user.id)}, {"$set": user.to_dict()})

    def delete(self, user_id: str) -> None:
        self.collection.delete_one({"_id": ObjectId(user_id)})

    def find_all(self) -> list[User]:
        users_data = self.collection.find({})
        return [User.from_dict(user_data) for user_data in users_data]
