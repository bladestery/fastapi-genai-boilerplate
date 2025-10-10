"""Schemas for the monitor API."""

from pydantic import BaseModel, Field

from app.core.enums import LogLevel


class LoggerLevelRequestParams(BaseModel):
    """Logger level schema."""

    log_level: LogLevel = Field(
        default=LogLevel.DEBUG,
        description="The desired log level for the application logger. "
        "Valid values: debug, info, warning, error, critical, trace.",
    )
