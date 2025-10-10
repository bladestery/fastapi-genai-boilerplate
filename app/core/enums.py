"""Application enums."""

import enum


class LogLevel(str, enum.Enum):
    """Defines available logging levels for application monitoring and debugging."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    TRACE = "TRACE"


class CacheBackend(str, enum.Enum):
    """Supported cache backends."""

    REDIS = "redis"
    LOCAL = "local"


class RateLimitBackend(str, enum.Enum):
    """Supported rate-limit backends."""

    REDIS = "redis"
    LOCAL = "local"


class AppEnvs(str, enum.Enum):
    """Application envs"""

    LOCAL = "local"
    DEVELOPMENT = "development"
    QA = "qa"
    DEMO = "demo"
    PRODUCTION = "production"
