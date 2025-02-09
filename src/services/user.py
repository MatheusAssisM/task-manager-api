from typing import Optional, List
from ..repositories.user import UserRepository
from ..models.user import User
from ..services.auth import AuthService


class UserService:
    def __init__(self, user_repository: UserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID"""
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email"""
        return self.user_repository.find_by_email(email)

    def get_all_users(self) -> List[User]:
        """Retrieve all users"""
        return self.user_repository.find_all()

    def update_user(self, user_id: str, username: str = None, email: str = None, password: str = None) -> User:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        
        if username:
            user.username = username
        if email and email != user.email:
            if self.get_user_by_email(email):
                raise ValueError("Email already in use")
            user.email = email
        if password:
            user.password = self.auth_service._hash_password(password)

        self.user_repository.update(user_id, user)
        return user

    def delete_user(self, user_id: str) -> None:
        """Delete user by ID"""
        if not self.user_repository.find_by_id(user_id):
            raise ValueError("User not found")
        self.user_repository.delete(user_id)
