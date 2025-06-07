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


class AppEnvs(str, enum.Enum):
    """Application envs"""

    DEVELOPMENT = "development"
    QA = "qa"
    DEMO = "demo"
    PRODUCTION = "production"


class AppConfig(BaseSettings):
    """Primary configuration settings for the application."""

    # Logging configuration
    log_level: LogLevel = LogLevel.DEBUG

    # Application metadata
    release_version: str = "0.0.1"
    environment: AppEnvs = AppEnvs.DEVELOPMENT
    host: str = "0.0.0.0"
    port: int = 8002
    worker_count: int | None = None

    class Config:
        """Configuration for environment file loading."""

        env_file = ".env"
        env_file_encoding = "utf-8"


# Initialize configuration settings
settings = AppConfig()
