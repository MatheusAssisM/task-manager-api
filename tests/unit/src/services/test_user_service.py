import pytest
from unittest.mock import Mock
from src.services.user import UserService
from src.models.user import User


@pytest.fixture
def user_repository():
    return Mock()


@pytest.fixture
def auth_service():
    return Mock()


@pytest.fixture
def user_service(user_repository, auth_service):
    return UserService(user_repository, auth_service)


@pytest.fixture
def sample_user():
    return User(
        id="test_id",
        username="test_user",
        email="test@example.com",
        password="hashed_password",
    )


def test_get_user_by_id_success(user_service, user_repository, sample_user):
    # Arrange
    user_repository.find_by_id.return_value = sample_user

    # Act
    result = user_service.get_user_by_id(sample_user.id)

    # Assert
    assert result == sample_user
    user_repository.find_by_id.assert_called_once_with(sample_user.id)


def test_get_user_by_id_not_found(user_service, user_repository):
    # Arrange
    user_repository.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="User not found"):
        user_service.get_user_by_id("nonexistent_id")


def test_get_user_by_email(user_service, user_repository, sample_user):
    # Arrange
    user_repository.find_by_email.return_value = sample_user

    # Act
    result = user_service.get_user_by_email(sample_user.email)

    # Assert
    assert result == sample_user
    user_repository.find_by_email.assert_called_once_with(sample_user.email)


def test_get_all_users(user_service, user_repository, sample_user):
    # Arrange
    users = [sample_user]
    user_repository.find_all.return_value = users

    # Act
    result = user_service.get_all_users()

    # Assert
    assert result == users
    user_repository.find_all.assert_called_once()


def test_update_user_username_only(user_service, user_repository, sample_user):
    # Arrange
    user_repository.find_by_id.return_value = sample_user

    # Act
    result = user_service.update_user(user_id=sample_user.id, username="new_username")

    # Assert
    assert result.username == "new_username"
    assert result.email == sample_user.email
    user_repository.update.assert_called_once_with(sample_user.id, result)


def test_update_user_email_exists(user_service, user_repository, sample_user):
    # Arrange
    user_repository.find_by_id.return_value = sample_user
    existing_user = Mock(id="other_id", email="new@example.com")
    user_repository.find_by_email.return_value = existing_user

    # Act & Assert
    with pytest.raises(ValueError, match="Email already in use"):
        user_service.update_user(user_id=sample_user.id, email="new@example.com")


def test_update_user_password(user_service, user_repository, auth_service, sample_user):
    # Arrange
    user_repository.find_by_id.return_value = sample_user
    auth_service._hash_password.return_value = "new_hashed_password"

    # Act
    result = user_service.update_user(user_id=sample_user.id, password="new_password")

    # Assert
    assert result.password == "new_hashed_password"
    auth_service._hash_password.assert_called_once_with("new_password")
    user_repository.update.assert_called_once_with(sample_user.id, result)


def test_delete_user_success(user_service, user_repository, sample_user):
    # Arrange
    user_repository.find_by_id.return_value = sample_user

    # Act
    user_service.delete_user(sample_user.id)

    # Assert
    user_repository.delete.assert_called_once_with(sample_user.id)


def test_delete_user_not_found(user_service, user_repository):
    # Arrange
    user_repository.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="User not found"):
        user_service.delete_user("nonexistent_id")
