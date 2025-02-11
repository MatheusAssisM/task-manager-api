from flask import Flask, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from src.config import Config
from src.extensions import init_app
from src.routes.task import tasks_bp
from src.routes.auth import auth_bp
from src.routes.metrics import metrics_bp
from src.swagger import swagger_config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.url_map.strict_slashes = False
    
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
            r"/*": {},
        }
    )

    init_app(app)

    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(metrics_bp, url_prefix="/metrics")

    SWAGGER_URL = '/api/docs'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        None,
        config={
            'app_name': "Task Manager API",
            'spec': swagger_config
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route('/api/swagger.json')
    def swagger_json():
        return jsonify(swagger_config)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
