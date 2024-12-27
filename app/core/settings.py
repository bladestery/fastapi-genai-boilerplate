"""Configuration settings for the application"""

import enum

from pydantic_settings import BaseSettings


class LogLevel(str, enum.Enum):
    """Defines available logging levels for application monitoring and debugging."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class AppConfig(BaseSettings):
    """Primary configuration settings for the application."""

    # Logging configuration
    log_level: LogLevel = LogLevel.DEBUG

    # Application metadata
    release_version: str = "0.0.1"
    environment: str = "dev"
    host: str = "0.0.0.0"
    port: int = 8001
    worker_count: int = 1

    class Config:
        """Configuration for environment file loading."""

        env_file = ".env"
        env_file_encoding = "utf-8"


# Initialize configuration settings
settings = AppConfig()
