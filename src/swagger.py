swagger_config = {
    "swagger": "2.0",
    "info": {
        "title": "Task Manager API",
        "description": "A RESTful API for managing tasks with authentication and metrics",
        "version": "1.0.0",
        "contact": {
            "email": "noreply@taskmanager.com"
        }
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token format: Bearer <token>"
        }
    },
    "paths": {
        "/auth/register": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Register a new user",
                "parameters": [{
                    "in": "body",
                    "name": "body",
                    "description": "User registration details",
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "example": "john_doe"},
                            "email": {"type": "string", "example": "john@example.com"},
                            "password": {"type": "string", "example": "securepass123"}
                        }
                    }
                }],
                "responses": {
                    "201": {"description": "User registered successfully"},
                    "400": {"description": "Invalid input"}
                }
            }
        },
        "/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Login to get access token",
                "parameters": [{
                    "in": "body",
                    "name": "body",
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "example": "john@example.com"},
                            "password": {"type": "string", "example": "securepass123"}
                        }
                    }
                }],
                "responses": {
                    "200": {"description": "Login successful"},
                    "401": {"description": "Invalid credentials"}
                }
            }
        },
        "/tasks": {
            "get": {
                "tags": ["Tasks"],
                "summary": "Get all tasks for authenticated user",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {"description": "List of tasks"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "post": {
                "tags": ["Tasks"],
                "summary": "Create a new task",
                "security": [{"Bearer": []}],
                "parameters": [{
                    "in": "body",
                    "name": "body",
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "example": "Complete project"},
                            "description": {"type": "string", "example": "Finish the documentation"}
                        }
                    }
                }],
                "responses": {
                    "201": {"description": "Task created"},
                    "400": {"description": "Invalid input"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/tasks/{task_id}": {
            "parameters": [{
                "in": "path",
                "name": "task_id",
                "required": True,
                "type": "string",
                "description": "ID of the task"
            }],
            "get": {
                "tags": ["Tasks"],
                "summary": "Get a specific task",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {"description": "Task details"},
                    "404": {"description": "Task not found"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "put": {
                "tags": ["Tasks"],
                "summary": "Update a task",
                "security": [{"Bearer": []}],
                "parameters": [{
                    "in": "body",
                    "name": "body",
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    }
                }],
                "responses": {
                    "200": {"description": "Task updated"},
                    "404": {"description": "Task not found"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "delete": {
                "tags": ["Tasks"],
                "summary": "Delete a task",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {"description": "Task deleted"},
                    "404": {"description": "Task not found"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/tasks/{task_id}/status": {
            "parameters": [{
                "in": "path",
                "name": "task_id",
                "required": True,
                "type": "string",
                "description": "ID of the task"
            }],
            "patch": {
                "tags": ["Tasks"],
                "summary": "Update task completion status",
                "security": [{"Bearer": []}],
                "parameters": [{
                    "in": "body",
                    "name": "body",
                    "required": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "completed": {"type": "boolean"}
                        }
                    }
                }],
                "responses": {
                    "200": {"description": "Task status updated"},
                    "404": {"description": "Task not found"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/metrics": {
            "get": {
                "tags": ["Metrics"],
                "summary": "Get system metrics",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {"description": "System metrics"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
    }
}