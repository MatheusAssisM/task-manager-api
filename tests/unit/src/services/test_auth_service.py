import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json
from jose import jwt

from src.config import Config
from src.services.auth import AuthService
from src.models.user import User


@pytest.fixture
def user_repository():
    return Mock()


@pytest.fixture
def redis_client():
    mock = Mock()
    # Set up scan_iter to return empty list by default
    mock.scan_iter.return_value = []
    # Set up get to return None by default
    mock.get.return_value = None
    return mock


@pytest.fixture
def email_service():
    return Mock()


@pytest.fixture
def auth_service(user_repository, redis_client, email_service):
    return AuthService(user_repository, redis_client, email_service)


@pytest.fixture
def test_user():
    return User(
        id="test_id",
        username="test_user",
        email="test@example.com",
        password="hashed_password",
    )


def test_register_success(auth_service, user_repository):
    # Arrange
    user_repository.find_by_email.return_value = None
    user_repository.create.return_value = "new_user_id"

    # Act
    new_user = auth_service.register(
        username="new_user", email="new@example.com", password="password123"
    )

    # Assert
    assert new_user.username == "new_user"
    assert new_user.email == "new@example.com"
    assert new_user.id == "new_user_id"
    assert new_user.password != "password123"  # Password should be hashed


def test_register_existing_email(auth_service, user_repository, test_user):
    # Arrange
    user_repository.find_by_email.return_value = test_user

    # Act & Assert
    with pytest.raises(ValueError, match="Email already registered"):
        auth_service.register(
            username="new_user", email="test@example.com", password="password123"
        )


def test_authenticate_success(auth_service, user_repository, test_user, redis_client):
    # Arrange
    user_repository.find_by_email.return_value = test_user
    redis_client.scan_iter.return_value = []  # No existing tokens
    
    with patch("bcrypt.checkpw", return_value=True):
        # Act
        authenticated_user = auth_service.authenticate(
            email="test@example.com", password="correct_password"
        )

        # Assert
        assert authenticated_user == test_user


def test_authenticate_invalid_password(auth_service, user_repository, test_user):
    # Arrange
    user_repository.find_by_email.return_value = test_user
    with patch("bcrypt.checkpw", return_value=False):
        # Act
        authenticated_user = auth_service.authenticate(
            email="test@example.com", password="wrong_password"
        )

        # Assert
        assert authenticated_user is None


def test_authenticate_user_not_found(auth_service, user_repository):
    # Arrange
    user_repository.find_by_email.return_value = None

    # Act
    authenticated_user = auth_service.authenticate(
        email="nonexistent@example.com", password="password123"
    )

    # Assert
    assert authenticated_user is None


def test_create_access_token(auth_service, test_user):
    # Act
    token_data = auth_service.create_access_token(test_user)

    # Assert
    assert "access_token" in token_data
    assert token_data["expires_in"] > 0

    # Verify token contents
    decoded = jwt.decode(
        token_data["access_token"],
        Config.JWT_SECRET_KEY,
        algorithms=[Config.JWT_ALGORITHM],
    )
    assert decoded["sub"] == test_user.id
    assert decoded["email"] == test_user.email


def test_validate_token_success(auth_service, user_repository, test_user, redis_client):
    # Arrange
    token = jwt.encode(
        {
            "sub": test_user.id,
            "email": test_user.email,
            "exp": datetime.utcnow()
            + timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )
    
    # Mock Redis to return cached user data
    cached_data = json.dumps({
        "user_id": test_user.id,
        "email": test_user.email,
        "username": test_user.username
    }).encode('utf-8')
    redis_client.get.return_value = cached_data
    
    user_repository.find_by_id.return_value = test_user

    # Act
    validated_user = auth_service.validate_token(token)

    # Assert
    assert validated_user == test_user


def test_validate_token_expired(auth_service, redis_client):
    # Arrange
    token = jwt.encode(
        {
            "sub": "test_id",
            "email": "test@example.com",
            "exp": datetime.utcnow() - timedelta(minutes=1),
        },
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )
    redis_client.get.return_value = None

    # Act
    validated_user = auth_service.validate_token(token)

    # Assert
    assert validated_user is None


def test_validate_token_invalid(auth_service, redis_client):
    # Arrange
    redis_client.get.return_value = None
    
    # Act
    validated_user = auth_service.validate_token("invalid_token")

    # Assert
    assert validated_user is None
