from dependency_injector import containers, providers
from pymongo import MongoClient
from redis import StrictRedis
from .services.task import TaskService
from .services.cached_task import CachedTaskService
from .services.auth import AuthService
from .services.user import UserService
from .services.email import EmailService
from .services.metrics import MetricsService
from .repositories.task import TaskRepository
from .repositories.user import UserRepository
from .repositories.metrics import MetricsRepository


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Database clients
    mongo_client = providers.Singleton(
        MongoClient,
        host=config.mongo.host,
        port=config.mongo.port,
        username=config.mongo.username,
        password=config.mongo.password,
    )

    redis_client = providers.Singleton(
        StrictRedis,
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        password=config.redis.password,
    )

    # Database
    mongo_db = providers.Singleton(
        lambda client, db_name: client.get_database(db_name),
        client=mongo_client,
        db_name=config.mongo.db_name,
    )

    # Repositories
    metrics_repository = providers.Factory(
        MetricsRepository,
        collection=providers.Singleton(
            lambda db: db.get_collection("metrics"), db=mongo_db
        ),
    )

    task_repository = providers.Factory(
        TaskRepository,
        collection=providers.Singleton(
            lambda db: db.get_collection("tasks"), db=mongo_db
        ),
    )

    user_repository = providers.Factory(
        UserRepository,
        collection=providers.Singleton(
            lambda db: db.get_collection("users"), db=mongo_db
        ),
    )

    # Services
    email_service = providers.Factory(EmailService)

    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        redis_client=redis_client,
        email_service=email_service,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        auth_service=auth_service,
    )

    # Core task service
    core_task_service = providers.Factory(
        TaskService,
        task_repository=task_repository,
        user_service=user_service,
    )

    # Cached task service that wraps the core task service
    task_service = providers.Factory(
        CachedTaskService,
        task_service=core_task_service,
        redis_client=redis_client,
    )

    metrics_service = providers.Factory(
        MetricsService,
        metrics_repository=metrics_repository,
        task_repository=task_repository,
        user_repository=user_repository,
    )
