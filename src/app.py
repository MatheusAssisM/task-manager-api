from flask import Flask
from flask_cors import CORS
from src.config import Config
from src.extensions import init_app
from src.routes.task import tasks_bp
from src.routes.auth import auth_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(
        app,
        resources={
            r"/*": {
                "origins": ["http://localhost:9000"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    # Initialize extensions and container
    init_app(app)

    # Register blueprints
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
