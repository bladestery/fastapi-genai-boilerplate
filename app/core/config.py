"""Configuration settings for the application"""

import enum
from typing import Union

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, enum.Enum):
    """Defines available logging levels for application monitoring and debugging."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    TRACE = "TRACE"


class AppEnvs(str, enum.Enum):
    """Application envs"""

    DEVELOPMENT = "development"
    QA = "qa"
    DEMO = "demo"
    PRODUCTION = "production"


class AppConfig(BaseSettings):
    """Primary configuration settings for the application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    log_level: LogLevel = LogLevel.TRACE
    release_version: str = "0.0.1"
    environment: AppEnvs = AppEnvs.DEVELOPMENT
    host: str = "0.0.0.0"
    port: int = 8002
    worker_count: Union[int, None] = None


# Initialize configuration settings
settings = AppConfig()
