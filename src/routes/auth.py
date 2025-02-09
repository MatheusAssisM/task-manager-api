from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.services.auth import AuthService
from src.schemas.user import UserRegister, UserLogin, UserResponse
from functools import wraps


auth_bp = Blueprint("auth", __name__)


def validate_request(schema_class):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                json_data = request.get_json()
                validated_data = schema_class(**json_data)
                return f(validated_data, *args, **kwargs)
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        return decorated_function

    return decorator


@auth_bp.route("/register", methods=["POST"])
@inject
@validate_request(UserRegister)
def register(
    data: UserRegister, auth_service: AuthService = Provide[Container.auth_service]
):
    try:
        user = auth_service.register(
            username=data.username, email=data.email, password=data.password
        )
        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": UserResponse(
                        id=user.id, username=user.username, email=user.email
                    ).model_dump(),
                }
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/login", methods=["POST"])
@inject
@validate_request(UserLogin)
def login(data: UserLogin, auth_service: AuthService = Provide[Container.auth_service]):
    try:
        user = auth_service.authenticate(data.email, data.password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        token_data = auth_service.create_access_token(user)
        return (
            jsonify(
                {
                    "message": "Login successful",
                    "user": UserResponse(
                        id=user.id, username=user.username, email=user.email
                    ).model_dump(),
                    **token_data,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/validate-token", methods=["GET"])
@inject
def validate_token(auth_service: AuthService = Provide[Container.auth_service]):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(" ")[1]
    user = auth_service.validate_token(token)

    if not user:
        return jsonify({"error": "Invalid or expired token"}), 401

    return (
        jsonify(
            {
                "valid": True,
                "user": UserResponse(
                    id=user.id, username=user.username, email=user.email
                ).model_dump(),
            }
        ),
        200,
    )
