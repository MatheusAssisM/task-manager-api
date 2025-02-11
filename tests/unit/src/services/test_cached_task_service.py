import pytest
from unittest.mock import Mock
import json
from src.services.cached_task import CachedTaskService
from src.models.task import Task


@pytest.fixture
def task_service():
    return Mock()


@pytest.fixture
def redis_client():
    return Mock()


@pytest.fixture
def cached_task_service(task_service, redis_client):
    return CachedTaskService(task_service, redis_client)


@pytest.fixture
def sample_task():
    return Task(
        id="test_id",
        title="Test Task",
        description="Test Description",
        user_id="test_user",
        completed=False,
    )


def test_create_task(cached_task_service, task_service, redis_client):
    # Arrange
    task_service.create_task.return_value = "new_task_id"

    # Act
    result = cached_task_service.create_task(
        title="New Task", description="New Description", user_id="user123"
    )

    # Assert
    task_service.create_task.assert_called_once_with(
        "New Task", "New Description", "user123"
    )
    redis_client.delete.assert_called_once_with("user_tasks:user123")
    assert result == "new_task_id"


def test_get_task_from_cache(cached_task_service, redis_client, sample_task):
    # Arrange
    cached_data = json.dumps(
        {
            "id": sample_task.id,
            "title": sample_task.title,
            "description": sample_task.description,
            "user_id": sample_task.user_id,
            "completed": sample_task.completed,
        }
    )
    redis_client.get.return_value = cached_data

    # Act
    result = cached_task_service.get_task(sample_task.id, sample_task.user_id)

    # Assert
    redis_client.get.assert_called_once_with(f"task:{sample_task.id}")
    assert result.id == sample_task.id
    assert result.title == sample_task.title
    assert result.description == sample_task.description
    assert result.user_id == sample_task.user_id


def test_get_task_unauthorized(cached_task_service, redis_client, sample_task):
    # Arrange
    cached_data = json.dumps(
        {
            "id": sample_task.id,
            "title": sample_task.title,
            "description": sample_task.description,
            "user_id": sample_task.user_id,
            "completed": sample_task.completed,
        }
    )
    redis_client.get.return_value = cached_data

    # Act & Assert
    with pytest.raises(ValueError, match="Unauthorized access to task"):
        cached_task_service.get_task(sample_task.id, "wrong_user")


def test_get_task_from_service(
    cached_task_service, task_service, redis_client, sample_task
):
    # Arrange
    redis_client.get.return_value = None
    task_service.get_task.return_value = sample_task

    # Act
    result = cached_task_service.get_task(sample_task.id, sample_task.user_id)

    # Assert
    task_service.get_task.assert_called_once_with(sample_task.id, sample_task.user_id)
    assert result == sample_task


def test_update_task(cached_task_service, task_service, redis_client, sample_task):
    # Act
    cached_task_service.update_task(
        task_id=sample_task.id,
        title="Updated Title",
        description="Updated Description",
        user_id=sample_task.user_id,
    )

    # Assert
    task_service.update_task.assert_called_once_with(
        sample_task.id, "Updated Title", "Updated Description", sample_task.user_id
    )
    redis_client.delete.assert_any_call(f"task:{sample_task.id}")
    redis_client.delete.assert_any_call(f"user_tasks:{sample_task.user_id}")


def test_get_user_tasks_from_cache(cached_task_service, redis_client):
    # Arrange
    tasks_data = [
        {
            "id": "task1",
            "title": "Task 1",
            "description": "Description 1",
            "user_id": "user123",
            "completed": False,
        },
        {
            "id": "task2",
            "title": "Task 2",
            "description": "Description 2",
            "user_id": "user123",
            "completed": True,
        },
    ]
    redis_client.get.return_value = json.dumps(tasks_data)

    # Act
    results = cached_task_service.get_user_tasks("user123")

    # Assert
    assert len(results) == 2
    assert results[0].id == "task1"
    assert results[1].id == "task2"
    assert results[0].completed == False
    assert results[1].completed == True


def test_get_user_tasks_from_service(cached_task_service, task_service, redis_client):
    # Arrange
    redis_client.get.return_value = None
    tasks = [
        Task(
            id="task1",
            title="Task 1",
            description="Description 1",
            user_id="user123",
            completed=False,
        ),
        Task(
            id="task2",
            title="Task 2",
            description="Description 2",
            user_id="user123",
            completed=True,
        ),
    ]
    task_service.get_user_tasks.return_value = tasks

    # Act
    results = cached_task_service.get_user_tasks("user123")

    # Assert
    task_service.get_user_tasks.assert_called_once_with("user123")
    assert len(results) == 2
    assert results == tasks
