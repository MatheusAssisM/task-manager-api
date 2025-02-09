import pytest
from unittest.mock import Mock, MagicMock
from bson.objectid import ObjectId
from src.repositories.user import UserRepository
from src.models.user import User


@pytest.fixture
def mock_collection():
    return Mock()


@pytest.fixture
def user_repository(mock_collection):
    return UserRepository(mock_collection)


@pytest.fixture
def sample_user():
    return User(
        username="test_user",
        email="test@example.com",
        password="hashed_password"
    )


@pytest.fixture
def sample_user_dict():
    return {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "username": "test_user",
        "email": "test@example.com",
        "password": "hashed_password"
    }


def test_create_user(user_repository, mock_collection, sample_user):
    # Arrange
    expected_id = "507f1f77bcf86cd799439011"
    mock_collection.insert_one.return_value = MagicMock(inserted_id=ObjectId(expected_id))

    # Act
    user_id = user_repository.create(sample_user)

    # Assert
    assert user_id == expected_id
    mock_collection.insert_one.assert_called_once_with(sample_user.to_dict())


def test_find_by_id_existing_user(user_repository, mock_collection, sample_user_dict):
    # Arrange
    user_id = "507f1f77bcf86cd799439011"
    mock_collection.find_one.return_value = sample_user_dict

    # Act
    user = user_repository.find_by_id(user_id)

    # Assert
    assert user is not None
    assert user.username == sample_user_dict["username"]
    assert user.email == sample_user_dict["email"]
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(user_id)})


def test_find_by_id_non_existing_user(user_repository, mock_collection):
    # Arrange
    user_id = "507f1f77bcf86cd799439011"
    mock_collection.find_one.return_value = None

    # Act
    user = user_repository.find_by_id(user_id)

    # Assert
    assert user is None
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(user_id)})


def test_find_by_email_existing_user(user_repository, mock_collection, sample_user_dict):
    # Arrange
    email = "test@example.com"
    mock_collection.find_one.return_value = sample_user_dict

    # Act
    user = user_repository.find_by_email(email)

    # Assert
    assert user is not None
    assert user.email == email
    mock_collection.find_one.assert_called_once_with({"email": email})


def test_find_by_email_non_existing_user(user_repository, mock_collection):
    # Arrange
    email = "nonexistent@example.com"
    mock_collection.find_one.return_value = None

    # Act
    user = user_repository.find_by_email(email)

    # Assert
    assert user is None
    mock_collection.find_one.assert_called_once_with({"email": email})


def test_update_user(user_repository, mock_collection, sample_user):
    # Arrange
    user_id = "507f1f77bcf86cd799439011"

    # Act
    user_repository.update(user_id, sample_user)

    # Assert
    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(user_id)},
        {"$set": sample_user.to_dict()}
    )


def test_delete_user(user_repository, mock_collection):
    # Arrange
    user_id = "507f1f77bcf86cd799439011"

    # Act
    user_repository.delete(user_id)

    # Assert
    mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(user_id)})


def test_find_all_users(user_repository, mock_collection, sample_user_dict):
    # Arrange
    mock_collection.find.return_value = [sample_user_dict, sample_user_dict]

    # Act
    users = user_repository.find_all()

    # Assert
    assert len(users) == 2
    assert all(isinstance(user, User) for user in users)
    mock_collection.find.assert_called_once_with({})
