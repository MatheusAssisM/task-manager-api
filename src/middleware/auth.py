from functools import wraps
from flask import request, jsonify
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

        if not auth_header:
            return jsonify({"error": "No authorization header"}), 401

        try:
            # Expecting "Bearer <token>"
            token_type, token = auth_header.split()
            if token_type.lower() != "bearer":
                return jsonify({"error": "Invalid token type"}), 401

            # Verify and decode token
            decoded_token = auth_service.verify_token(token)

            # Add user_id to kwargs so the route can access it
            kwargs["current_user_id"] = decoded_token["user_id"]
            return f(*args, **kwargs)

        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401

    return decorated_function
