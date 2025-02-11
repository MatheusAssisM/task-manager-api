from flask import Blueprint, request, jsonify, g
from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.services.auth import AuthService
from src.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    UserRegisterResponse,
    UserLoginResponse,
    UserLogoutResponse,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    PasswordReset,
    PasswordResetResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from src.schemas.common import ErrorResponse, UnauthorizedResponse
from src.utils.decorators import validate_request
from src.middleware.auth import require_auth


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
                UserRegisterResponse(
                    user=UserResponse(
                        id=user.id, username=user.username, email=user.email
                    )
                ).model_dump()
            ),
            201,
        )
    except ValueError as e:
        return jsonify(ErrorResponse(error=str(e)).model_dump()), 400
    except Exception as e:
        return jsonify(ErrorResponse(error="Internal server error").model_dump()), 500


@auth_bp.route("/login", methods=["POST"])
@inject
@validate_request(UserLogin)
def login(data: UserLogin, auth_service: AuthService = Provide[Container.auth_service]):
    try:
        user = auth_service.authenticate(data.email, data.password)
        if not user:
            return (
                jsonify(UnauthorizedResponse(error="Invalid credentials").model_dump()),
                401,
            )

        token_data = auth_service.create_tokens(user)
        return (
            jsonify(
                UserLoginResponse(
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    expires_in=token_data["expires_in"],
                    user=UserResponse(
                        id=user.id, username=user.username, email=user.email
                    ),
                ).model_dump()
            ),
            200,
        )
    except Exception as e:
        return jsonify(ErrorResponse(error="Internal server error").model_dump()), 500


@auth_bp.route("/refresh", methods=["POST"])
@inject
@validate_request(RefreshTokenRequest)
def refresh_token(
    data: RefreshTokenRequest, auth_service: AuthService = Provide[Container.auth_service]
):
    try:
        token_data = auth_service.refresh_access_token(data.refresh_token)
        if not token_data:
            return (
                jsonify(UnauthorizedResponse(error="Invalid refresh token").model_dump()),
                401,
            )

        # Get user info
        user = auth_service.validate_token(token_data["access_token"])
        return (
            jsonify(
                RefreshTokenResponse(
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    expires_in=token_data["expires_in"],
                    user=UserResponse(
                        id=user.id, username=user.username, email=user.email
                    ),
                ).model_dump()
            ),
            200,
        )
    except Exception as e:
        return jsonify(ErrorResponse(error="Internal server error").model_dump()), 500


@auth_bp.route("/logout", methods=["POST"])
@require_auth
@inject
def logout(auth_service: AuthService = Provide[Container.auth_service]):
    token = g.token
    if auth_service.logout(token):
        return jsonify(UserLogoutResponse().model_dump()), 200
    return (
        jsonify(UnauthorizedResponse(error="Invalid or expired token").model_dump()),
        401,
    )


@auth_bp.route("/forgot-password", methods=["POST"])
@inject
@validate_request(PasswordResetRequest)
def forgot_password(
    data: PasswordResetRequest,
    auth_service: AuthService = Provide[Container.auth_service],
):
    auth_service.request_password_reset(data.email)
    return jsonify(PasswordResetRequestResponse().model_dump()), 200


@auth_bp.route("/reset-password", methods=["POST"])
@inject
@validate_request(PasswordReset)
def reset_password(
    data: PasswordReset, auth_service: AuthService = Provide[Container.auth_service]
):
    if auth_service.reset_password(data.token, data.new_password):
        return jsonify(PasswordResetResponse().model_dump()), 200
    return (
        jsonify(ErrorResponse(error="Invalid or expired reset token").model_dump()),
        400,
    )
