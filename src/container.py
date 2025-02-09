from dependency_injector import containers, providers
from pymongo import MongoClient
from redis import StrictRedis
from .services.task import TaskService
from .repositories.task import TaskRepository


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Database clients
    mongo_client = providers.Singleton(MongoClient, config.mongo.uri)

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

    # Services
    task_service = providers.Factory(TaskService, task_repository=task_repository)
