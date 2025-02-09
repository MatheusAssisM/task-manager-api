from dependency_injector import containers, providers
from pymongo import MongoClient
from redis import StrictRedis
from .services.task import TaskService
from .services.auth import AuthService
from .services.user import UserService
from .repositories.task import TaskRepository
from .repositories.user import UserRepository


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
    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        redis_client=redis_client,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        auth_service=auth_service,
    )

    task_service = providers.Factory(
        TaskService,
        task_repository=task_repository,
        user_service=user_service,
    )
