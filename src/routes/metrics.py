from flask import Blueprint, jsonify
from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.services.metrics import MetricsService
from src.middleware.auth import require_auth
from src.utils.logger import setup_logger

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
        return jsonify(metrics.to_dict()), 200
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
