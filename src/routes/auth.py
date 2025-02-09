from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.services.auth import AuthService
from src.schemas.user import UserRegister, UserLogin, UserResponse
from src.utils.decorators import validate_request
from src.middleware.auth import require_auth
from flask import g


auth_bp = Blueprint("auth", __name__)


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
                    **token_data,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/logout", methods=["POST"])
@require_auth
@inject
def logout(auth_service: AuthService = Provide[Container.auth_service]):
    token = g.token
    if auth_service.logout(token):
        return jsonify({"message": "Successfully logged out"}), 200
    return jsonify({"error": "Invalid or expired token"}), 401
