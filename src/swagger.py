swagger_config = {
    "swagger": "2.0",
    "info": {
        "title": "Task Manager API",
        "description": "A RESTful API for managing tasks with authentication and metrics",
        "version": "1.0.0",
        "contact": {"email": "noreply@taskmanager.com"},
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token format: Bearer <token>",
        }
    },
    "paths": {
        "/auth/register": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Register a new user",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "description": "User registration details",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["username", "email", "password"],
                            "properties": {
                                "username": {
                                    "type": "string",
                                    "minLength": 3,
                                    "maxLength": 50,
                                    "example": "john_doe",
                                },
                                "email": {
                                    "type": "string",
                                    "format": "email",
                                    "example": "john@example.com",
                                },
                                "password": {
                                    "type": "string",
                                    "minLength": 6,
                                    "example": "securepass123",
                                },
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {
                        "description": "User registered successfully",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"},
                                "user": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "username": {"type": "string"},
                                        "email": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    "400": {"description": "Invalid input"},
                },
            }
        },
        "/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Login to get access token",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["email", "password"],
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "format": "email",
                                    "example": "john@example.com",
                                },
                                "password": {
                                    "type": "string",
                                    "example": "securepass123",
                                },
                            },
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "access_token": {"type": "string"},
                                "expires_in": {"type": "integer"},
                                "user": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "username": {"type": "string"},
                                        "email": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    "401": {"description": "Invalid credentials"},
                },
            }
        },
        "/auth/logout": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Logout current user",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {
                        "description": "Successfully logged out",
                        "schema": {
                            "type": "object",
                            "properties": {"message": {"type": "string"}},
                        },
                    },
                    "401": {"description": "Unauthorized"},
                },
            }
        },
        "/auth/forgot-password": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Request password reset",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["email"],
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "format": "email",
                                    "example": "john@example.com",
                                }
                            },
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Password reset email sent",
                        "schema": {
                            "type": "object",
                            "properties": {"message": {"type": "string"}},
                        },
                    }
                },
            }
        },
        "/auth/reset-password": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Reset password with token",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["token", "new_password"],
                            "properties": {
                                "token": {"type": "string"},
                                "new_password": {"type": "string", "minLength": 6},
                            },
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Password reset successful",
                        "schema": {
                            "type": "object",
                            "properties": {"message": {"type": "string"}},
                        },
                    },
                    "400": {"description": "Invalid token or password"},
                },
            }
        },
        "/tasks": {
            "get": {
                "tags": ["Tasks"],
                "summary": "Get all tasks for authenticated user",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {
                        "description": "List of tasks",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "tasks": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "title": {"type": "string"},
                                            "description": {"type": "string"},
                                            "user_id": {"type": "string"},
                                            "completed": {"type": "boolean"},
                                        },
                                    },
                                }
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                },
            },
            "post": {
                "tags": ["Tasks"],
                "summary": "Create a new task",
                "security": [{"Bearer": []}],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["title", "description"],
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 100,
                                    "example": "Complete project",
                                },
                                "description": {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 500,
                                    "example": "Finish the documentation",
                                },
                            },
                        },
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Task created",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"},
                                "id": {"type": "string"},
                            },
                        },
                    },
                    "400": {"description": "Invalid input"},
                    "401": {"description": "Unauthorized"},
                },
            },
        },
        "/tasks/{task_id}": {
            "parameters": [
                {
                    "in": "path",
                    "name": "task_id",
                    "required": True,
                    "type": "string",
                    "description": "ID of the task",
                }
            ],
            "get": {
                "tags": ["Tasks"],
                "summary": "Get a specific task",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {
                        "description": "Task details",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "user_id": {"type": "string"},
                                "completed": {"type": "boolean"},
                            },
                        },
                    },
                    "404": {"description": "Task not found"},
                    "401": {"description": "Unauthorized"},
                },
            },
            "put": {
                "tags": ["Tasks"],
                "summary": "Update a task",
                "security": [{"Bearer": []}],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 100,
                                },
                                "description": {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 500,
                                },
                            },
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Task updated",
                        "schema": {
                            "type": "object",
                            "properties": {"message": {"type": "string"}},
                        },
                    },
                    "404": {"description": "Task not found"},
                    "401": {"description": "Unauthorized"},
                },
            },
            "delete": {
                "tags": ["Tasks"],
                "summary": "Delete a task",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {
                        "description": "Task deleted",
                        "schema": {
                            "type": "object",
                            "properties": {"message": {"type": "string"}},
                        },
                    },
                    "404": {"description": "Task not found"},
                    "401": {"description": "Unauthorized"},
                },
            },
        },
        "/tasks/{task_id}/status": {
            "parameters": [
                {
                    "in": "path",
                    "name": "task_id",
                    "required": True,
                    "type": "string",
                    "description": "ID of the task",
                }
            ],
            "patch": {
                "tags": ["Tasks"],
                "summary": "Update task completion status",
                "security": [{"Bearer": []}],
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["completed"],
                            "properties": {"completed": {"type": "boolean"}},
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Task status updated",
                        "schema": {
                            "type": "object",
                            "properties": {"message": {"type": "string"}},
                        },
                    },
                    "404": {"description": "Task not found"},
                    "401": {"description": "Unauthorized"},
                },
            },
        },
        "/metrics": {
            "get": {
                "tags": ["Metrics"],
                "summary": "Get system metrics",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {
                        "description": "System metrics",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "total_users": {"type": "integer"},
                                "total_tasks": {"type": "integer"},
                                "completed_tasks": {"type": "integer"},
                                "active_tasks": {"type": "integer"},
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "500": {
                        "description": "Internal server error",
                        "schema": {
                            "type": "object",
                            "properties": {"error": {"type": "string"}},
                        },
                    },
                },
            }
        },
    },
}
