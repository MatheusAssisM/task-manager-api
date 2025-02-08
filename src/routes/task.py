from flask import Blueprint, request, jsonify, abort
from dependency_injector.wiring import inject, Provide
from src.container import Container
from src.services.task import TaskService
from src.schemas.task import TaskCreate, TaskUpdate
from pydantic import ValidationError
from functools import wraps

tasks_bp = Blueprint('tasks', __name__)

def validate_request(schema_class):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                json_data = request.get_json()
                validated_data = schema_class(**json_data)
                return f(validated_data, *args, **kwargs)
            except ValidationError as e:
                return jsonify({"error": "Validation error", "details": e.errors()}), 400
        return decorated_function
    return decorator

@tasks_bp.route('/tasks', methods=['POST'])
@inject
@validate_request(TaskCreate)
def create(data: TaskCreate, task_service: TaskService = Provide[Container.task_service]):
    task_id = task_service.create_task(data.title, data.description)
    return jsonify({'message': 'Task created successfully', 'id': task_id}), 201

@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
@inject
def retrieve(task_id: str, task_service: TaskService = Provide[Container.task_service]):
    try:
        task = task_service.get_task(task_id)
        if task:
            return jsonify({'id': task.id, **task.to_dict()}), 200
        return jsonify({'message': 'Task not found'}), 404
    except ValueError as e:
        abort(400, description=str(e))

@tasks_bp.route('/tasks/<task_id>', methods=['PUT'])
@inject
@validate_request(TaskUpdate)
def update(data: TaskUpdate, task_id: str, task_service: TaskService = Provide[Container.task_service]):
    task_service.update_task(
        task_id,
        data.title if data.title is not None else task_service.get_task(task_id).title,
        data.description if data.description is not None else task_service.get_task(task_id).description
    )
    return jsonify({'message': 'Task updated successfully'}), 200

@tasks_bp.route('/tasks/<task_id>', methods=['DELETE'])
@inject
def delete(task_id: str, task_service: TaskService = Provide[Container.task_service]):
    task_service.delete_task(task_id)
    return jsonify({'message': 'Task deleted successfully'}), 200

@tasks_bp.route('/tasks', methods=['GET'])
@inject
def list_tasks(task_service: TaskService = Provide[Container.task_service]):
    tasks = task_service.get_all_tasks()
    tasks_response = [{'id': task.id, **task.to_dict()} for task in tasks]
    return jsonify(tasks_response), 200