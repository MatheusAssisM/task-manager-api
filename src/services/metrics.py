from ..repositories.metrics import MetricsRepository
from ..repositories.task import TaskRepository
from ..repositories.user import UserRepository
from ..models.metrics import Metrics
from ..utils.logger import setup_logger

logger = setup_logger('metrics_service')

class MetricsService:
    def __init__(self, metrics_repository: MetricsRepository, 
                 task_repository: TaskRepository,
                 user_repository: UserRepository):
        self.metrics_repository = metrics_repository
        self.task_repository = task_repository
        self.user_repository = user_repository

    def get_metrics(self) -> Metrics:
        """Get current metrics from repositories and update stored metrics"""
        try:
            # Get all tasks and users
            tasks = self.task_repository.find_all()
            total_users = len(self.user_repository.find_all())
            
            # Calculate task metrics
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task.completed)
            active_tasks = total_tasks - completed_tasks
            
            # Create new metrics object
            metrics = Metrics(
                total_users=total_users,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                active_tasks=active_tasks
            )
            
            # Update stored metrics
            self.metrics_repository.update_metrics(metrics)
            
            logger.info("Metrics updated successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
            # Return last known metrics if available, otherwise return empty metrics
            stored_metrics = self.metrics_repository.get_metrics()
            return stored_metrics if stored_metrics else Metrics()