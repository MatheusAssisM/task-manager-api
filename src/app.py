from flask import Flask
from flask_cors import CORS
from src.config import Config
from src.extensions import init_app
from src.routes.task import tasks_bp
from src.routes.auth import auth_bp
from src.routes.metrics import metrics_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Disable automatic slash behavior
    app.url_map.strict_slashes = False
    
    # Updated CORS configuration
    CORS(
        app,
        origins=["http://localhost:9000"],
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ],
        expose_headers=[
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Credentials"
        ],
        resources={
            r"/*": {},  # Match all task routes including sub-routes
        }
    )

    # Initialize extensions and container
    init_app(app)

    # Register blueprints (without trailing slashes)
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(metrics_bp, url_prefix="/metrics")

    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
