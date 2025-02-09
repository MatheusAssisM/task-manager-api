from functools import wraps
from flask import request, jsonify
from pydantic import ValidationError


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
                return jsonify({"error": str(e)}), 400

        return decorated_function

    return decorator
