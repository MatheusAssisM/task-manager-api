import pytest
from unittest.mock import Mock, MagicMock
from bson.objectid import ObjectId
from src.models.user import User
from src.models.task import Task
from src.services.task import TaskService
from src.services.auth import AuthService
from src.services.metrics import MetricsService


@pytest.fixture
def valid_object_id():
    return "507f1f77bcf86cd799439011"


@pytest.fixture
def mock_collection():
    return MagicMock()


# User fixtures
@pytest.fixture
def user_repository():
    return Mock()


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
        "password": "hashed_password",
    }


@pytest.fixture
def test_user():
    return User(
        id="test_id",
        username="test_user",
        email="test@example.com",
        password="hashed_password",
    )


# Task fixtures
@pytest.fixture
def task_repository():
    return MagicMock()


@pytest.fixture
def sample_task():
    return Task(
        title="Test Task",
        description="Test Description",
        user_id="test_user_id"
    )


@pytest.fixture
def sample_task_dict():
    return {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "title": "Test Task",
        "description": "Test Description",
    }


# Service fixtures
@pytest.fixture
def user_service():
    return Mock()


@pytest.fixture
def task_service(task_repository, user_service):
    return TaskService(task_repository, user_service)


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


# Metrics fixtures
@pytest.fixture
def metrics_repository():
    return Mock()


@pytest.fixture
def metrics_service(metrics_repository, task_repository, user_repository):
    return MetricsService(metrics_repository, task_repository, user_repository)