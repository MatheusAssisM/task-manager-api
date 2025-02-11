# Task Manager API

## Overview

Task Manager API is a robust Flask-based RESTful service that provides task management functionality with user authentication. The application uses MongoDB for persistent storage and Redis for caching and session management, making it both scalable and performant.

## Features

- 🔐 User Authentication (register, login, logout)
- 📝 Complete Task Management (CRUD operations)
- 📊 Metrics and Analytics
- 🔄 Redis Caching for improved performance
- 🗄️ MongoDB for persistent storage
- 🔒 Password reset functionality
- 🌐 CORS support for frontend integration

## Tech Stack

- **Framework**: Flask 3.0+
- **Database**: MongoDB
- **Caching**: Redis
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: OpenAPI/Swagger
- **Dependencies**: 
  - dependency-injector for DI
  - pydantic for data validation
  - Flask-PyMongo for MongoDB integration
  - Flask-CORS for CORS support

## Prerequisites

- Python 3.10+
- MongoDB
- Redis
- Docker (optional)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/task-manager-api.git
   cd task-manager-api
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   The default configuration in `.env.example` is ready for Docker usage. If you're running locally, you might need to adjust the host values.

## Running the Application

### Using Docker Compose (Recommended)
1. Start all services:
   ```bash
   docker-compose up --build
   ```

2. The following services will be available:
   - API: `http://localhost:8000`
   - MongoDB: `localhost:27017`
   - Redis: `localhost:6379`
   - Mailhog GUI: `http://localhost:8025` (for viewing sent emails)

3. You can monitor email notifications (like password reset emails) through the Mailhog web interface at `http://localhost:8025`

### Local Development
If you prefer to run the application locally without Docker:

1. Make sure MongoDB and Redis are running locally
2. Update the `.env` file to use `localhost` instead of service names
3. Run the application:
   ```bash
   python src/app.py
   ```
   The API will be available at `http://localhost:8000`

## API Documentation

The API is documented using OpenAPI/Swagger. You can access the interactive API documentation at:

- Local development: `http://localhost:8000/api/docs`
- Docker: Same URL after starting the containers

The Swagger UI provides:
- Interactive API documentation
- Request/response examples
- API endpoint testing interface
- Authentication flow documentation
- Model schemas and validation rules

The raw Swagger JSON specification is available at `/api/docs`.

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `POST /auth/logout` - Logout and invalidate token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

### Tasks
- `GET /tasks` - List all tasks
- `POST /tasks` - Create a new task
- `GET /tasks/<id>` - Get task details
- `PUT /tasks/<id>` - Update a task
- `DELETE /tasks/<id>` - Delete a task

### Metrics
- `GET /metrics` - Get system metrics and statistics

## Development

### Running Tests
```bash
pytest
```

For test coverage report:
```bash
pytest --cov=src tests/
```

### Code Formatting
```bash
black src/
```

## Docker Support

The application includes Docker support for easy deployment:

1. Build the image:
   ```bash
   docker build -t task-manager-api .
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up
   ```

This will start the API service along with MongoDB and Redis containers.

## CORS Configuration

The API is configured to accept requests from `http://localhost:9000` by default. To modify CORS settings, update the configuration in `src/app.py`.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for details.