from unittest.mock import MagicMock
import pytest
from bson import ObjectId
from src.repositories.task import TaskRepository
from src.models.task import Task


@pytest.fixture
def mock_collection():
    return MagicMock()


@pytest.fixture
def task_repository(mock_collection):
    return TaskRepository(mock_collection)


@pytest.fixture
def sample_task():
    return Task(title="Test Task", description="Test Description", user_id="test_user_id")


@pytest.fixture
def sample_task_dict():
    return {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "title": "Test Task",
        "description": "Test Description",
    }


def test_create_task(task_repository, sample_task, mock_collection):
    # Arrange
    expected_id = "507f1f77bcf86cd799439011"
    mock_collection.insert_one.return_value.inserted_id = ObjectId(expected_id)

    # Act
    result = task_repository.create(sample_task)

    # Assert
    assert result == expected_id
    mock_collection.insert_one.assert_called_once_with(sample_task.to_dict())


def test_find_by_id_existing_task(task_repository, sample_task_dict, mock_collection):
    # Arrange
    task_id = str(sample_task_dict["_id"])
    mock_collection.find_one.return_value = sample_task_dict

    # Act
    result = task_repository.find_by_id(task_id)

    # Assert
    assert isinstance(result, Task)
    assert result.title == sample_task_dict["title"]
    assert result.description == sample_task_dict["description"]
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(task_id)})


def test_find_by_id_non_existing_task(task_repository, mock_collection):
    # Arrange
    task_id = "507f1f77bcf86cd799439011"
    mock_collection.find_one.return_value = None

    # Act
    result = task_repository.find_by_id(task_id)

    # Assert
    assert result is None
    mock_collection.find_one.assert_called_once_with({"_id": ObjectId(task_id)})


def test_update_task(task_repository, sample_task, mock_collection):
    # Arrange
    task_id = "507f1f77bcf86cd799439011"

    # Act
    task_repository.update(task_id, sample_task)

    # Assert
    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(task_id)}, {"$set": sample_task.to_dict()}
    )


def test_delete_task(task_repository, mock_collection):
    # Arrange
    task_id = "507f1f77bcf86cd799439011"

    # Act
    task_repository.delete(task_id)

    # Assert
    mock_collection.delete_one.assert_called_once_with({"_id": ObjectId(task_id)})


def test_find_all_tasks(task_repository, sample_task_dict, mock_collection):
    # Arrange
    mock_collection.find.return_value = [sample_task_dict, sample_task_dict]

    # Act
    results = task_repository.find_all()

    # Assert
    assert len(results) == 2
    assert all(isinstance(task, Task) for task in results)
    assert all(task.title == sample_task_dict["title"] for task in results)
    assert all(task.description == sample_task_dict["description"] for task in results)
    mock_collection.find.assert_called_once_with({})
