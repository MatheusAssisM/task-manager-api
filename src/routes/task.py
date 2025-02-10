from flask import Blueprint, jsonify, g
from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.services.task import TaskService
from src.schemas.task import TaskCreate, TaskUpdate
from src.middleware.auth import require_auth
from src.utils.decorators import validate_request
from src.utils.logger import setup_logger

logger = setup_logger('task_routes')
tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/", methods=["POST"])
@inject
@require_auth
@validate_request(TaskCreate)
def create(
    data: TaskCreate,
    task_service: TaskService = Provide[Container.task_service],
):
    try:
        task_id = task_service.create_task(
            data.title, data.description, g.current_user.id
        )
        logger.info(f"Successfully created task {task_id} for user {g.current_user.id}")
        return jsonify({"message": "Task created successfully", "id": task_id}), 201
    except ValueError as e:
        logger.error(f"Validation error while creating task: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Unexpected error while creating task")
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route("/<task_id>", methods=["GET"])
@inject
@require_auth
def retrieve(
    task_id: str,
    task_service: TaskService = Provide[Container.task_service],
):
    try:
        task = task_service.get_task(task_id, g.current_user.id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({"id": task.id, **task.to_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route("/<task_id>", methods=["PUT"])
@inject
@require_auth
@validate_request(TaskUpdate)
def update(
    data: TaskUpdate,
    task_id: str,
    task_service: TaskService = Provide[Container.task_service],
):
    try:
        task = task_service.get_task(task_id, g.current_user.id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404

        task_service.update_task(task_id, data.title, data.description)
        return jsonify({"message": "Task updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route("/<task_id>", methods=["DELETE"])
@inject
@require_auth
def delete(
    task_id: str,
    task_service: TaskService = Provide[Container.task_service],
):
    try:
        task = task_service.get_task(task_id, g.current_user.id)
        if task is None:
            logger.warning(f"Attempt to delete non-existent task: {task_id}")
            return jsonify({"error": "Task not found"}), 404

        task_service.delete_task(task_id, g.current_user.id)  # Added user_id parameter
        logger.info(f"Task {task_id} successfully deleted by user {g.current_user.id}")
        return jsonify({"message": "Task deleted successfully"}), 200
    except ValueError as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception(f"Unexpected error deleting task {task_id}")
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route("/user/tasks", methods=["GET"])
@inject
@require_auth
def get_user_tasks(task_service: TaskService = Provide[Container.task_service]):
    try:
        tasks = task_service.get_user_tasks(g.current_user.id)
        tasks_response = [{"id": task.id, **task.to_dict()} for task in tasks]
        logger.info(f"Retrieved {len(tasks)} tasks for user {g.current_user.id}")
        return jsonify(tasks_response), 200
    except Exception as e:
        logger.exception("Error retrieving user tasks")
        return jsonify({"error": "Internal server error"}), 500
