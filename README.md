# README.md for task-manager-api

# Task Manager API

## Overview

Task Manager API is a Flask application that allows users to manage tasks with support for MongoDB and Redis. This API provides endpoints for creating, retrieving, updating, and deleting tasks, making it easy to integrate task management into your applications.

## Features

- Create, read, update, and delete tasks
- MongoDB for persistent storage
- Redis for caching and session management

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/task-manager-api.git
   ```

2. Navigate to the project directory:

   ```
   cd task-manager-api
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:

```
python src/app.py
```

The API will be available at `http://localhost:5000`.

## API Endpoints

- `POST /tasks`: Create a new task
- `GET /tasks`: Retrieve all tasks
- `GET /tasks/<id>`: Retrieve a task by ID
- `PUT /tasks/<id>`: Update a task by ID
- `DELETE /tasks/<id>`: Delete a task by ID

## Running Tests

To run the tests, use the following command:

```
pytest
```

## Docker

To build and run the application using Docker, execute the following commands:

```
docker build -t task-manager-api .
docker run -p 5000:5000 task-manager-api
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.