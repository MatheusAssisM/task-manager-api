from flask import Flask
from .container import Container
from urllib.parse import urlparse

container = Container()


def init_app(app: Flask) -> None:
    """Initialize all application extensions"""
    # Parse MongoDB URI to get database name
    mongo_uri = app.config["MONGO_URI"]
    parsed_uri = urlparse(mongo_uri)
    db_name = parsed_uri.path.lstrip("/") or "task_manager"

    container.config.from_dict(
        {
            "mongo": {"uri": mongo_uri, "db_name": db_name},
            "redis": {"host": "localhost", "port": 6379, "db": 0},
        }
    )

    # Wire the container
    container.wire(packages=["src"])

    # Add container to app
    app.container = container
