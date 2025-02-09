from flask import Blueprint, request, jsonify, abort
from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.services.task import TaskService
from src.schemas.task import TaskCreate, TaskUpdate
from pydantic import ValidationError
from functools import wraps
from src.middleware.auth import require_auth

tasks_bp = Blueprint("tasks", __name__)


def validate_request(schema_class):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                json_data = request.get_json()
                validated_data = schema_class(**json_data)
                return f(validated_data, *args, **kwargs)
            except ValidationError as e:
                return (
                    jsonify({"error": "Validation error", "details": e.errors()}),
                    400,
                )
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        return decorated_function

    return decorator


@tasks_bp.route("/", methods=["POST"])
@inject
@require_auth
@validate_request(TaskCreate)
def create(
    data: TaskCreate,
    current_user_id: str,
    task_service: TaskService = Provide[Container.task_service]
):
    try:
        task_id = task_service.create_task(data.title, data.description, current_user_id)
        return jsonify({"message": "Task created successfully", "id": task_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route("/<task_id>", methods=["GET"])
@inject
@require_auth
def retrieve(
    task_id: str,
    current_user_id: str,
    task_service: TaskService = Provide[Container.task_service]
):
    try:
        task = task_service.get_task(task_id, current_user_id)
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
    current_user_id: str,
    task_service: TaskService = Provide[Container.task_service],
):
    try:
        task = task_service.get_task(task_id, current_user_id)
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
    current_user_id: str,
    task_service: TaskService = Provide[Container.task_service]
):
    try:
        task = task_service.get_task(task_id, current_user_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404

        task_service.delete_task(task_id)
        return jsonify({"message": "Task deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route("/user/tasks", methods=["GET"])
@inject
@require_auth
def get_user_tasks(
    current_user_id: str,
    task_service: TaskService = Provide[Container.task_service]
):
    try:
        tasks = task_service.get_user_tasks(current_user_id)
        tasks_response = [{"id": task.id, **task.to_dict()} for task in tasks]
        return jsonify(tasks_response), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
