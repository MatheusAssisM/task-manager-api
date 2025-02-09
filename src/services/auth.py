from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from ..models.user import User
from ..repositories.user import UserRepository

# Configuration constants
SECRET_KEY = "your-secret-key"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    def register(self, username: str, email: str, password: str) -> User:
        # Check if user already exists
        if self.user_repository.find_by_email(email):
            raise ValueError("Email already registered")

        hashed_password = self._hash_password(password)
        user = User(username=username, email=email, password=hashed_password)
        user.id = self.user_repository.create(user)
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.user_repository.find_by_email(email)
        if not user:
            return None
        if not self._verify_password(password, user.password):
            return None
        return user

    def create_access_token(self, user: User) -> dict:
        claims = {
            "sub": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        token = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def validate_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                return None
            return self.user_repository.find_by_id(user_id)
        except JWTError:
            return None