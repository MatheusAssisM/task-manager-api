from unittest.mock import MagicMock
import pytest
from src.services.task import TaskService
from src.models.task import Task


@pytest.fixture
def valid_object_id():
    return "507f1f77bcf86cd799439011"


@pytest.fixture
def task_repository():
    return MagicMock()


@pytest.fixture
def user_service():
    return MagicMock()


@pytest.fixture
def task_service(task_repository, user_service):
    return TaskService(task_repository, user_service)


def test_create_task_success(task_service):
    # Arrange
    title = "New Task"
    description = "New Description"
    user_id = "test_user_id"
    task_service.task_repository.create.return_value = "507f1f77bcf86cd799439011"

    # Act
    result = task_service.create_task(title, description, user_id)

    # Assert
    assert isinstance(result, str)
    task_service.task_repository.create.assert_called_once()
    args = task_service.task_repository.create.call_args[0][0]
    assert isinstance(args, Task)
    assert args.title == title
    assert args.description == description
    assert args.user_id == user_id
    assert args.completed is False


def test_update_task_not_found(task_service, valid_object_id):
    # Arrange
    task_service.task_repository.find_by_id.return_value = None
    user_id = "test_user_id"

    # Act & Assert
    with pytest.raises(ValueError, match="Task not found"):
        task_service.update_task(valid_object_id, "Updated Title", "Updated Description", user_id)


def test_delete_task_not_found(task_service, valid_object_id):
    # Arrange
    task_service.task_repository.find_by_id.return_value = None
    user_id = "test_user_id"

    # Act & Assert
    with pytest.raises(ValueError, match="Task not found"):
        task_service.delete_task(valid_object_id, user_id)


def test_create_task_with_empty_title(task_service):
    # Arrange
    title = ""
    description = "Some description"
    user_id = "test_user_id"

    # Act & Assert
    with pytest.raises(ValueError, match="Title cannot be empty"):
        task_service.create_task(title, description, user_id)


def test_get_task_success(task_service, valid_object_id):
    # Arrange
    task = Task(
        title="Test Task",
        description="Test Description",
        user_id="test_user_id",
        id=valid_object_id,
    )
    task_service.task_repository.find_by_id.return_value = task

    # Act
    result = task_service.get_task(valid_object_id, "test_user_id")

    # Assert
    assert result.id == valid_object_id
    assert result.title == "Test Task"
    assert result.description == "Test Description"
    assert result.user_id == "test_user_id"


def test_get_task_invalid_id(task_service):
    # Arrange
    invalid_id = "invalid_id"
    user_id = "test_user_id"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid task ID format"):
        task_service.get_task(invalid_id, user_id)


def test_get_task_unauthorized(task_service, valid_object_id):
    # Arrange
    task = Task(
        title="Test Task",
        description="Test Description",
        user_id="different_user_id",
        id=valid_object_id,
    )
    task_service.task_repository.find_by_id.return_value = task

    # Act & Assert
    with pytest.raises(ValueError, match="Unauthorized access to task"):
        task_service.get_task(valid_object_id, "test_user_id")


def test_get_all_tasks_success(task_service):
    # Arrange
    user_id = "test_user_id"
    expected_tasks = [
        Task(title="Test Task 1", description="Description 1", user_id=user_id),
        Task(title="Test Task 2", description="Description 2", user_id=user_id),
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
    existing_task = Task(
        id=valid_object_id,
        title="Old Title",
        description="Old Description",
        user_id="test_user_id",
        completed=True
    )
    task_service.task_repository.find_by_id.return_value = existing_task
    new_title = "Updated Task"
    new_description = "Updated Description"

    # Act
    task_service.update_task(valid_object_id, new_title, new_description, "test_user_id")

    # Assert
    task_service.task_repository.update.assert_called_once()
    updated_task = task_service.task_repository.update.call_args[0][1]
    assert updated_task.title == new_title
    assert updated_task.description == new_description
    assert updated_task.user_id == "test_user_id"
    assert updated_task.completed == True  # Completion status should be preserved


def test_delete_task_success(task_service, valid_object_id):
    # Arrange
    existing_task = Task(
        id=valid_object_id,
        title="Task",
        description="Description",
        user_id="test_user_id",
    )
    task_service.task_repository.find_by_id.return_value = existing_task

    # Act
    task_service.delete_task(valid_object_id, "test_user_id")

    # Assert
    task_service.task_repository.delete.assert_called_once_with(valid_object_id)


def test_update_task_invalid_id(task_service):
    # Arrange
    invalid_id = "invalid_id"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid task ID format"):
        task_service.update_task(invalid_id, "Title", "Description", "test_user_id")


def test_delete_task_invalid_id(task_service):
    # Arrange
    invalid_id = "invalid_id"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid task ID format"):
        task_service.delete_task(invalid_id, "test_user_id")


def test_update_task_unauthorized(task_service, valid_object_id):
    # Arrange
    existing_task = Task(
        id=valid_object_id,
        title="Task",
        description="Description",
        user_id="different_user_id",
    )
    task_service.task_repository.find_by_id.return_value = existing_task

    # Act & Assert
    with pytest.raises(ValueError, match="Unauthorized access to task"):
        task_service.update_task(valid_object_id, "New Title", "New Description", "test_user_id")


def test_delete_task_unauthorized(task_service, valid_object_id):
    # Arrange
    existing_task = Task(
        id=valid_object_id,
        title="Task",
        description="Description",
        user_id="different_user_id",
    )
    task_service.task_repository.find_by_id.return_value = existing_task

    # Act & Assert
    with pytest.raises(ValueError, match="Unauthorized access to task"):
        task_service.delete_task(valid_object_id, "test_user_id")


def test_update_task_status_success(task_service, valid_object_id):
    # Arrange
    existing_task = Task(
        id=valid_object_id,
        title="Task",
        description="Description",
        user_id="test_user_id",
        completed=False
    )
    task_service.task_repository.find_by_id.return_value = existing_task

    # Act
    task_service.update_task_status(valid_object_id, True, "test_user_id")

    # Assert
    task_service.task_repository.update.assert_called_once()
    updated_task = task_service.task_repository.update.call_args[0][1]
    assert updated_task.completed is True
    assert updated_task.title == existing_task.title
    assert updated_task.description == existing_task.description
    assert updated_task.user_id == existing_task.user_id


def test_update_task_status_unauthorized(task_service, valid_object_id):
    # Arrange
    existing_task = Task(
        id=valid_object_id,
        title="Task",
        description="Description",
        user_id="different_user_id",
        completed=False
    )
    task_service.task_repository.find_by_id.return_value = existing_task

    # Act & Assert
    with pytest.raises(ValueError, match="Unauthorized access to task"):
        task_service.update_task_status(valid_object_id, True, "test_user_id")


def test_update_task_status_not_found(task_service, valid_object_id):
    # Arrange
    task_service.task_repository.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="Task not found"):
        task_service.update_task_status(valid_object_id, True, "test_user_id")


def test_update_task_status_invalid_id(task_service):
    # Arrange
    invalid_id = "invalid_id"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid task ID format"):
        task_service.update_task_status(invalid_id, True, "test_user_id")


def test_get_user_tasks_success(task_service):
    # Arrange
    user_id = "test_user_id"
    expected_tasks = [
        Task(title="Task 1", description="Description 1", user_id=user_id),
        Task(title="Task 2", description="Description 2", user_id=user_id),
    ]
    task_service.task_repository.find_by_user_id.return_value = expected_tasks

    # Act
    results = task_service.get_user_tasks(user_id)

    # Assert
    assert len(results) == 2
    assert all(isinstance(task, Task) for task in results)
    assert all(task.user_id == user_id for task in results)
    task_service.task_repository.find_by_user_id.assert_called_once_with(user_id)
