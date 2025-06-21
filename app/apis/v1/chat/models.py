"""Request module for chat streaming API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for configuring chat token streaming."""

    sleep: float = Field(
        1,
        json_schema_extra={
            "description": "Sleep duration (in seconds) between streamed tokens."
        },
    )
    number: int = Field(
        10, json_schema_extra={"description": "Total number of tokens to stream."}
    )
