import pytest
from unittest.mock import Mock
from src.models.metrics import Metrics
from src.models.task import Task
from src.models.user import User
from src.services.metrics import MetricsService


@pytest.fixture
def metrics_repository():
    return Mock()


@pytest.fixture
def task_repository():
    return Mock()


@pytest.fixture
def user_repository():
    return Mock()


@pytest.fixture
def metrics_service(metrics_repository, task_repository, user_repository):
    return MetricsService(metrics_repository, task_repository, user_repository)


def test_get_metrics_success(
    metrics_service,
    task_repository,
    user_repository,
    metrics_repository,
    sample_task,
    test_user,
):
    # Arrange
    tasks = [
        sample_task,  # Using fixture
        Task(
            title="Task 2", description="Desc 2", user_id=test_user.id, completed=False
        ),
        Task(title="Task 3", description="Desc 3", user_id="user2", completed=False),
    ]
    users = [test_user]  # Using fixture

    task_repository.find_all.return_value = tasks
    user_repository.find_all.return_value = users

    # Act
    result = metrics_service.get_metrics()

    # Assert
    assert result.total_users == 1
    assert result.total_tasks == 3
    assert result.completed_tasks == 0
    assert result.active_tasks == 3
    metrics_repository.update_metrics.assert_called_once()


def test_get_metrics_no_data(
    metrics_service, task_repository, user_repository, metrics_repository
):
    # Arrange
    task_repository.find_all.return_value = []
    user_repository.find_all.return_value = []

    # Act
    result = metrics_service.get_metrics()

    # Assert
    assert result.total_users == 0
    assert result.total_tasks == 0
    assert result.completed_tasks == 0
    assert result.active_tasks == 0
    metrics_repository.update_metrics.assert_called_once()


def test_get_metrics_with_error(metrics_service, task_repository, metrics_repository):
    # Arrange
    task_repository.find_all.side_effect = Exception("Database error")
    fallback_metrics = Metrics(total_users=1, total_tasks=1, completed_tasks=0)
    metrics_repository.get_metrics.return_value = fallback_metrics

    # Act
    result = metrics_service.get_metrics()

    # Assert
    assert result == fallback_metrics
    metrics_repository.get_metrics.assert_called_once()
    metrics_repository.update_metrics.assert_not_called()


def test_get_metrics_with_completed_tasks(
    metrics_service, task_repository, user_repository, metrics_repository, test_user
):
    # Arrange
    tasks = [
        Task(
            title="Task 1", description="Desc 1", user_id=test_user.id, completed=True
        ),
        Task(
            title="Task 2", description="Desc 2", user_id=test_user.id, completed=True
        ),
        Task(
            title="Task 3", description="Desc 3", user_id=test_user.id, completed=False
        ),
    ]
    users = [test_user]

    task_repository.find_all.return_value = tasks
    user_repository.find_all.return_value = users

    # Act
    result = metrics_service.get_metrics()

    # Assert
    assert result.total_users == 1
    assert result.total_tasks == 3
    assert result.completed_tasks == 2
    assert result.active_tasks == 1
    metrics_repository.update_metrics.assert_called_once()
