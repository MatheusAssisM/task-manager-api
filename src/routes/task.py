from flask import Blueprint, request, jsonify, abort
from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.services.task import TaskService
from src.schemas.task import TaskCreate, TaskUpdate
from pydantic import ValidationError
from functools import wraps

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
@validate_request(TaskCreate)
def create(
    data: TaskCreate, task_service: TaskService = Provide[Container.task_service]
):
    try:
        task_id = task_service.create_task(data.title, data.description)
        return jsonify({"message": "Task created successfully", "id": task_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route("/<task_id>", methods=["GET"])
@inject
def retrieve(task_id: str, task_service: TaskService = Provide[Container.task_service]):
    try:
        task = task_service.get_task(task_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({"id": task.id, **task.to_dict()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route("/<task_id>", methods=["PUT"])
@inject
@validate_request(TaskUpdate)
def update(
    data: TaskUpdate,
    task_id: str,
    task_service: TaskService = Provide[Container.task_service],
):
    try:
        current_task = task_service.get_task(task_id)
        if current_task is None:
            return jsonify({"error": "Task not found"}), 404

        task_service.update_task(
            task_id,
            data.title if data.title is not None else current_task.title,
            (
                data.description
                if data.description is not None
                else current_task.description
            ),
        )
        return jsonify({"message": "Task updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route("/<task_id>", methods=["DELETE"])
@inject
def delete(task_id: str, task_service: TaskService = Provide[Container.task_service]):
    try:
        task_service.delete_task(task_id)
        return jsonify({"message": "Task deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@tasks_bp.route("/", methods=["GET"])
@inject
def list_tasks(task_service: TaskService = Provide[Container.task_service]):
    try:
        tasks = task_service.get_all_tasks()
        tasks_response = [{"id": task.id, **task.to_dict()} for task in tasks]
        return jsonify(tasks_response), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
