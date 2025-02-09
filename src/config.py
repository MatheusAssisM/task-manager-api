import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/task_manager")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
