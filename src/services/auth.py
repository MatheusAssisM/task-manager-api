from datetime import datetime, timedelta
from typing import Optional
import json
import bcrypt
from jose import JWTError, jwt
from redis import StrictRedis
from ..models.user import User
from ..repositories.user import UserRepository
from ..config import Config


class AuthService:
    def __init__(self, user_repository: UserRepository, redis_client: StrictRedis):
        self.user_repository = user_repository
        self.redis_client = redis_client
        self.token_prefix = "token:"

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def register(self, username: str, email: str, password: str) -> User:
        # Check if user already exists
        if self.user_repository.find_by_email(email):
            raise ValueError("Email already registered")

        hashed_password = self._hash_password(password)
        user = User(username=username, email=email, password=hashed_password)
        user.id = self.user_repository.create(user)
        return user

    def _cleanup_previous_tokens(self, user_id: str) -> None:
        """Clean up any existing tokens for the user"""
        # Get all tokens
        for key in self.redis_client.scan_iter(f"{self.token_prefix}*"):
            data = self.redis_client.get(key)
            if data:
                user_data = json.loads(data.decode('utf-8'))
                if user_data.get('user_id') == user_id:
                    self.redis_client.delete(key)

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.user_repository.find_by_email(email)
        if not user:
            return None
        if not self._verify_password(password, user.password):
            return None
            
        # Clean up any existing tokens before creating a new one
        self._cleanup_previous_tokens(user.id)
        return user

    def create_access_token(self, user: User) -> dict:
        claims = {
            "sub": user.id,
            "email": user.email,
            "exp": datetime.utcnow()
            + timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        token = jwt.encode(
            claims, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM
        )
        
        # Store token data
        token_key = f"{self.token_prefix}{token}"
        user_data = {
            "user_id": user.id,
            "email": user.email,
            "username": user.username
        }

        expiration = Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        self.redis_client.setex(token_key, expiration, json.dumps(user_data))
        
        return {
            "access_token": token,
            "expires_in": expiration,
        }

    def validate_token(self, token: str) -> Optional[User]:
        cached_user = self.redis_client.get(f"{self.token_prefix}{token}")
        if cached_user:
            user_data = json.loads(cached_user)
            return self.user_repository.find_by_id(user_data["user_id"])
        return None

    def logout(self, token: str) -> bool:
        token_key = f"{self.token_prefix}{token}"
        if self.redis_client.delete(token_key):
            return True
        return False
