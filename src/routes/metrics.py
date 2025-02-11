from flask import Blueprint, jsonify
from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.services.metrics import MetricsService
from src.middleware.auth import require_auth
from src.utils.logger import setup_logger
from src.schemas.metrics import MetricsResponse, MetricsErrorResponse
from src.schemas.common import UnauthorizedResponse

logger = setup_logger("metrics_routes")
metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/", methods=["GET"])
@inject
@require_auth
def get_metrics(metrics_service: MetricsService = Provide[Container.metrics_service]):
    """Get current application metrics"""
    try:
        metrics = metrics_service.get_metrics()
        logger.info("Metrics retrieved successfully")
        return (
            jsonify(
                MetricsResponse(
                    total_users=metrics.total_users,
                    total_tasks=metrics.total_tasks,
                    completed_tasks=metrics.completed_tasks,
                    active_tasks=metrics.active_tasks,
                ).model_dump()
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return jsonify(MetricsErrorResponse().model_dump()), 500
