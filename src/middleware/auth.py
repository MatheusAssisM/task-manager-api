from functools import wraps
from flask import request, jsonify, g
from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.services.auth import AuthService


def require_auth(f):
    @wraps(f)
    @inject
    def decorated_function(
        *args, auth_service: AuthService = Provide[Container.auth_service], **kwargs
    ):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Invalid authorization header"}), 401

        token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"error": "No token provided"}), 401

        # Validate token and get user
        user = auth_service.validate_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Store user in flask g object for route access
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function
