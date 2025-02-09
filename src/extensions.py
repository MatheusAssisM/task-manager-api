from flask import Flask
from .container import Container

container = Container()


def init_app(app: Flask) -> None:
    """Initialize all application extensions"""
    container.config.from_dict(
        {
            "mongo": {
                "host": app.config["MONGO_HOST"],
                "port": int(app.config["MONGO_PORT"]),
                "db_name": app.config["MONGO_DB"],
                "username": app.config.get("MONGO_USERNAME"),
                "password": app.config.get("MONGO_PASSWORD"),
            },
            "redis": {
                "host": app.config["REDIS_HOST"],
                "port": int(app.config["REDIS_PORT"]),
                "db": int(app.config["REDIS_DB"]),
                "password": app.config.get("REDIS_PASSWORD"),
            },
        }
    )

    # Wire the container
    container.wire(packages=["src"])

    # Add container to app
    app.container = container
