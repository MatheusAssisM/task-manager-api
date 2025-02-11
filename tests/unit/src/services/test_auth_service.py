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


def test_create_tokens(auth_service, test_user, redis_client):
    # Act
    token_data = auth_service.create_tokens(test_user)

    # Assert
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["expires_in"] == Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # Verify access token
    decoded_access = jwt.decode(
        token_data["access_token"],
        Config.JWT_SECRET_KEY,
        algorithms=[Config.JWT_ALGORITHM],
    )
    assert decoded_access["sub"] == test_user.id
    assert decoded_access["email"] == test_user.email
    assert decoded_access["type"] == "access"

    # Verify refresh token
    decoded_refresh = jwt.decode(
        token_data["refresh_token"],
        Config.JWT_SECRET_KEY,
        algorithms=[Config.JWT_ALGORITHM],
    )
    assert decoded_refresh["sub"] == test_user.id
    assert decoded_refresh["email"] == test_user.email
    assert decoded_refresh["type"] == "refresh"

    # Verify tokens are stored in Redis
    redis_client.setex.assert_any_call(
        f"token:{token_data['access_token']}",
        Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        json.dumps({"user_id": test_user.id, "email": test_user.email, "username": test_user.username}),
    )

    redis_client.setex.assert_any_call(
        f"refresh:{token_data['refresh_token']}",
        7 * 24 * 60 * 60,  # 7 days in seconds
        json.dumps({"user_id": test_user.id, "email": test_user.email, "username": test_user.username}),
    )


def test_refresh_access_token_success(auth_service, test_user, redis_client):
    # Arrange
    refresh_token = jwt.encode(
        {
            "sub": test_user.id,
            "email": test_user.email,
            "exp": datetime.utcnow() + timedelta(days=7),
            "type": "refresh"
        },
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )

    # Mock Redis to return user data for the refresh token
    cached_data = json.dumps(
        {
            "user_id": test_user.id,
            "email": test_user.email,
            "username": test_user.username,
        }
    ).encode("utf-8")
    redis_client.get.return_value = cached_data

    # Set up user repository to return the user
    auth_service.user_repository.find_by_id.return_value = test_user

    # Act
    result = auth_service.refresh_access_token(refresh_token)

    # Assert
    assert result is not None
    assert "access_token" in result
    assert "refresh_token" in result
    assert "expires_in" in result

    # Verify new tokens
    decoded_access = jwt.decode(
        result["access_token"],
        Config.JWT_SECRET_KEY,
        algorithms=[Config.JWT_ALGORITHM],
    )
    assert decoded_access["sub"] == test_user.id
    assert decoded_access["type"] == "access"


def test_refresh_access_token_invalid_token(auth_service, redis_client):
    # Act
    result = auth_service.refresh_access_token("invalid_token")

    # Assert
    assert result is None


def test_refresh_access_token_wrong_type(auth_service, test_user, redis_client):
    # Arrange - Create a token with wrong type
    refresh_token = jwt.encode(
        {
            "sub": test_user.id,
            "email": test_user.email,
            "exp": datetime.utcnow() + timedelta(days=7),
            "type": "access"  # Wrong type
        },
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )

    # Act
    result = auth_service.refresh_access_token(refresh_token)

    # Assert
    assert result is None


def test_refresh_access_token_expired(auth_service, test_user):
    # Arrange - Create an expired token
    refresh_token = jwt.encode(
        {
            "sub": test_user.id,
            "email": test_user.email,
            "exp": datetime.utcnow() - timedelta(days=1),
            "type": "refresh"
        },
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )

    # Act
    result = auth_service.refresh_access_token(refresh_token)

    # Assert
    assert result is None


def test_validate_token_success(auth_service, user_repository, test_user, redis_client):
    # Arrange
    token = jwt.encode(
        {
            "sub": test_user.id,
            "email": test_user.email,
            "exp": datetime.utcnow() + timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access"
        },
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )

    # Mock Redis to return cached user data
    cached_data = json.dumps(
        {
            "user_id": test_user.id,
            "email": test_user.email,
            "username": test_user.username,
        }
    ).encode("utf-8")
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
            "type": "access"
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


def test_cleanup_previous_tokens(auth_service, redis_client, test_user):
    # Arrange
    # Mock Redis to return both access and refresh tokens
    token1 = "token:123"
    token2 = "token:456"
    refresh1 = "refresh:789"
    refresh2 = "refresh:012"
    redis_client.scan_iter.side_effect = [
        [token1, token2],  # First call for access tokens
        [refresh1, refresh2]  # Second call for refresh tokens
    ]

    # Setup mock data for each token
    token1_data = json.dumps(
        {
            "user_id": test_user.id,
            "email": test_user.email,
            "username": test_user.username,
        }
    ).encode("utf-8")
    token2_data = json.dumps(
        {
            "user_id": "other_user_id",
            "email": "other@example.com",
            "username": "other_user",
        }
    ).encode("utf-8")
    refresh1_data = json.dumps(
        {
            "user_id": test_user.id,
            "email": test_user.email,
            "username": test_user.username,
        }
    ).encode("utf-8")
    refresh2_data = json.dumps(
        {
            "user_id": "other_user_id",
            "email": "other@example.com",
            "username": "other_user",
        }
    ).encode("utf-8")

    def mock_get(key):
        if key == token1:
            return token1_data
        if key == token2:
            return token2_data
        if key == refresh1:
            return refresh1_data
        if key == refresh2:
            return refresh2_data
        return None

    redis_client.get.side_effect = mock_get

    # Act
    auth_service._cleanup_previous_tokens(test_user.id)

    # Assert
    # Should only delete tokens belonging to test_user
    redis_client.delete.assert_any_call(token1)
    redis_client.delete.assert_any_call(refresh1)
    assert redis_client.delete.call_count == 2


def test_logout_success(auth_service, redis_client):
    # Arrange
    token = jwt.encode(
        {
            "sub": "test_id",
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "type": "access"
        },
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )

    # Act
    result = auth_service.logout(token)

    # Assert
    assert result is True
    # Verify cleanup was called
    redis_client.scan_iter.assert_any_call("token:*")
    redis_client.scan_iter.assert_any_call("refresh:*")


def test_logout_token_not_found(auth_service, redis_client):
    # Arrange
    token = "invalid_token"
    redis_client.delete.return_value = 0  # Redis returns 0 when key doesn't exist

    # Act
    result = auth_service.logout(token)

    # Assert
    assert result is False
    redis_client.delete.assert_called_once_with(f"token:{token}")
