from datetime import datetime, timedelta
from typing import Optional, Dict
import json
import bcrypt
from jose import JWTError, jwt
from redis import StrictRedis
from ..models.user import User
from ..repositories.user import UserRepository
from ..config import Config
from src.services.email import EmailService


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        redis_client: StrictRedis,
        email_service: EmailService,
    ):
        self.user_repository = user_repository
        self.redis_client = redis_client
        self.token_prefix = "token:"
        self.refresh_token_prefix = "refresh:"
        self.email_service = email_service
        self.reset_prefix = "reset:"

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
                user_data = json.loads(data.decode("utf-8"))
                if user_data.get("user_id") == user_id:
                    self.redis_client.delete(key)
        
        # Clean up refresh tokens
        for key in self.redis_client.scan_iter(f"{self.refresh_token_prefix}*"):
            data = self.redis_client.get(key)
            if data:
                user_data = json.loads(data.decode("utf-8"))
                if user_data.get("user_id") == user_id:
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

    def create_tokens(self, user: User) -> Dict[str, any]:
        # Create access token
        access_token_expiry = datetime.utcnow() + timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token_claims = {
            "sub": user.id,
            "email": user.email,
            "exp": access_token_expiry,
            "type": "access"
        }
        access_token = jwt.encode(
            access_token_claims, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM
        )

        # Create refresh token with longer expiration
        refresh_token_expiry = datetime.utcnow() + timedelta(days=Config.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_claims = {
            "sub": user.id,
            "email": user.email,
            "exp": refresh_token_expiry,
            "type": "refresh"
        }
        refresh_token = jwt.encode(
            refresh_token_claims, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM
        )

        # Store token data
        user_data = {"user_id": user.id, "email": user.email, "username": user.username}
        
        # Store access token
        access_token_key = f"{self.token_prefix}{access_token}"
        self.redis_client.setex(
            access_token_key,
            Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            json.dumps(user_data)
        )

        # Store refresh token
        refresh_token_key = f"{self.refresh_token_prefix}{refresh_token}"
        self.redis_client.setex(
            refresh_token_key,
            Config.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # Convert days to seconds
            json.dumps(user_data)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, any]]:
        try:
            # Verify refresh token
            payload = jwt.decode(
                refresh_token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "refresh":
                return None

            # Check if refresh token is in Redis
            refresh_token_key = f"{self.refresh_token_prefix}{refresh_token}"
            cached_data = self.redis_client.get(refresh_token_key)
            
            if not cached_data:
                return None

            user_data = json.loads(cached_data)
            user = self.user_repository.find_by_id(payload["sub"])
            
            if not user:
                return None

            # Create new tokens
            return self.create_tokens(user)

        except JWTError:
            return None

    def validate_token(self, token: str) -> Optional[User]:
        try:
            # First check if token is in Redis
            cached_user = self.redis_client.get(f"{self.token_prefix}{token}")
            if not cached_user:
                return None

            # Verify JWT
            payload = jwt.decode(
                token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "access":
                return None

            user_data = json.loads(cached_user)
            return self.user_repository.find_by_id(user_data["user_id"])

        except JWTError:
            return None

    def logout(self, token: str) -> bool:
        try:
            payload = jwt.decode(
                token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
            )
            # Delete both access and refresh tokens for the user
            self._cleanup_previous_tokens(payload["sub"])
            return True
        except JWTError:
            token_key = f"{self.token_prefix}{token}"
            return bool(self.redis_client.delete(token_key))

    def request_password_reset(self, email: str) -> bool:
        user = self.user_repository.find_by_email(email)
        if not user:
            return False

        # Generate reset token
        reset_token = jwt.encode(
            {
                "sub": user.id,
                "exp": datetime.utcnow()
                + timedelta(minutes=Config.PASSWORD_RESET_EXPIRE_MINUTES),
            },
            Config.JWT_SECRET_KEY,
            algorithm=Config.JWT_ALGORITHM,
        )

        # Store token in Redis
        token_key = f"{self.reset_prefix}{reset_token}"
        self.redis_client.setex(
            token_key, Config.PASSWORD_RESET_EXPIRE_MINUTES * 60, user.id
        )

        # Send reset email
        reset_url = f"http://localhost:9000/reset-password?token={reset_token}"
        self.email_service.send_email(
            user.email,
            "Password Reset Request",
            f"Click the following link to reset your password: {reset_url}",
        )
        return True

    def reset_password(self, token: str, new_password: str) -> bool:
        token_key = f"{self.reset_prefix}{token}"
        user_id = self.redis_client.get(token_key)

        if not user_id:
            return False

        try:
            payload = jwt.decode(
                token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
            )
            user = self.user_repository.find_by_id(payload["sub"])
            if not user:
                return False

            # Update password
            hashed_password = self._hash_password(new_password)
            user.password = hashed_password
            self.user_repository.update(user.id, user)

            # Remove reset token
            self.redis_client.delete(token_key)
            return True

        except JWTError:
            return False
