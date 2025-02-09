import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

    # MongoDB Configuration
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    MONGO_DB = os.getenv("MONGO_DB", "task_manager")
    MONGO_USERNAME = os.getenv("MONGO_USERNAME", "")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    REDIS_DB = os.getenv("REDIS_DB", "0")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
