from flask import Flask
from src.config import Config
from src.extensions import init_app
from src.routes.task import tasks_bp  # Update this import

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions and container
    init_app(app)

    # Register blueprints
    app.register_blueprint(tasks_bp)

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)