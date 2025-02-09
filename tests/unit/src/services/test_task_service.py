from unittest.mock import Mock, patch, MagicMock
import pytest
from src.services.task import TaskService
from src.models.task import Task
from bson.objectid import ObjectId


@pytest.fixture
def sample_task_dict():
    return {"_id": "123", "title": "Test Task", "description": "Test Description"}


@pytest.fixture
def valid_object_id():
    return "507f1f77bcf86cd799439011"


@pytest.fixture
def task_repository():
    return MagicMock()


@pytest.fixture
def task_service(task_repository):
    return TaskService(task_repository)


def test_create_task_success(task_service):
    # Arrange
    title = "New Task"
    description = "New Description"
    expected_result = {
        "_id": "507f1f77bcf86cd799439011",
        "title": title,
        "description": description,
    }
    task_service.task_repository.create.return_value = expected_result

    # Act
    result = task_service.create_task(title, description)

    # Assert
    assert result == expected_result
    task_service.task_repository.create.assert_called_once()


def test_update_task_not_found(task_service, valid_object_id):
    # Arrange
    task_service.task_repository.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="Task not found"):
        task_service.update_task(
            valid_object_id, "Updated Title", "Updated Description"
        )


def test_delete_task_not_found(task_service, valid_object_id):
    # Arrange
    task_service.task_repository.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="Task not found"):
        task_service.delete_task(valid_object_id)


def test_create_task_with_empty_title(task_service):
    # Arrange
    title = ""
    description = "Some description"

    # Act & Assert
    with pytest.raises(ValueError, match="Title cannot be empty"):
        task_service.create_task(title, description)


def test_get_task_success(task_service, valid_object_id):
    # Arrange
    valid_object_id,
    task_service.task_repository.find_by_id.return_value = valid_object_id

    # Act
    result = task_service.get_task(valid_object_id)

    # Assert
    assert result == valid_object_id


def test_get_task_invalid_id(task_service):
    # Arrange
    invalid_id = "invalid_id"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid task ID format"):
        task_service.get_task(invalid_id)


def test_get_task_not_found(task_service, valid_object_id):
    # Arrange
    task_service.task_repository.find_by_id.return_value = None

    # Act
    result = task_service.get_task(valid_object_id)

    # Assert
    assert result is None


def test_get_all_tasks_success(task_service):
    # Arrange
    expected_tasks = [
        Task(title="Test Task 1", description="Description 1"),
        Task(title="Test Task 2", description="Description 2"),
    ]
    task_service.task_repository.find_all.return_value = expected_tasks

    # Act
    results = task_service.get_all_tasks()

    # Assert
    assert len(results) == 2
    assert all(isinstance(task, Task) for task in results)
    assert results == expected_tasks


def test_update_task_success(task_service, valid_object_id):
    # Arrange
    existing_task = {
        "_id": valid_object_id,
        "title": "Old Title",
        "description": "Old Description",
    }
    task_service.task_repository.find_by_id.return_value = existing_task
    new_title = "Updated Task"
    new_description = "Updated Description"

    # Act
    task_service.update_task(valid_object_id, new_title, new_description)

    # Assert
    task_service.task_repository.update.assert_called_once()


def test_delete_task_success(task_service, valid_object_id):
    # Arrange
    existing_task = {
        "_id": valid_object_id,
        "title": "Task",
        "description": "Description",
    }
    task_service.task_repository.find_by_id.return_value = existing_task

    # Act
    task_service.delete_task(valid_object_id)

    # Assert
    task_service.task_repository.delete.assert_called_once_with(valid_object_id)


def test_update_task_invalid_id(task_service):
    # Arrange
    invalid_id = "invalid_id"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid task ID format"):
        task_service.update_task(invalid_id, "Title", "Description")


def test_delete_task_invalid_id(task_service):
    # Arrange
    invalid_id = "invalid_id"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid task ID format"):
        task_service.delete_task(invalid_id)
