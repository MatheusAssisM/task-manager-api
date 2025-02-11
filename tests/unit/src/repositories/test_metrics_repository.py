import pytest
from unittest.mock import Mock, MagicMock
from bson import ObjectId
from src.repositories.metrics import MetricsRepository
from src.models.metrics import Metrics


@pytest.fixture
def collection():
    mock = MagicMock()
    # Configure the mock to handle ObjectId correctly
    mock.update_one = MagicMock()
    return mock


@pytest.fixture
def metrics_repository(collection):
    return MetricsRepository(collection)


def test_get_metrics_existing(metrics_repository, valid_object_id):
    # Arrange
    metrics_data = {
        "_id": ObjectId(valid_object_id),
        "total_users": 10,
        "total_tasks": 20,
        "completed_tasks": 15,
    }
    metrics_repository.collection.find_one.return_value = metrics_data

    # Act
    result = metrics_repository.get_metrics()

    # Assert
    assert isinstance(result, Metrics)
    assert result.total_users == 10
    assert result.total_tasks == 20
    assert result.completed_tasks == 15
    metrics_repository.collection.find_one.assert_called_once_with({})


def test_get_metrics_not_existing(metrics_repository):
    # Arrange
    metrics_repository.collection.find_one.return_value = None

    # Act
    result = metrics_repository.get_metrics()

    # Assert
    assert isinstance(result, Metrics)
    assert result.id is None
    assert result.total_users == 0
    assert result.total_tasks == 0
    assert result.completed_tasks == 0


def test_update_metrics_existing(metrics_repository, valid_object_id):
    # Arrange
    metrics_id = ObjectId(valid_object_id)
    metrics = Metrics(id=metrics_id, total_users=5, total_tasks=10, completed_tasks=7)

    # Act
    metrics_repository.update_metrics(metrics)

    # Assert
    metrics_repository.collection.update_one.assert_called_once()
    call_args = metrics_repository.collection.update_one.call_args[0]
    expected_filter = {"_id": metrics_id}
    assert call_args[0] == expected_filter
    assert call_args[1]["$set"] == metrics.to_dict()


def test_update_metrics_new(metrics_repository):
    # Arrange
    metrics = Metrics(total_users=5, total_tasks=10, completed_tasks=7)

    # Act
    metrics_repository.update_metrics(metrics)

    # Assert
    metrics_repository.collection.insert_one.assert_called_once_with(metrics.to_dict())
