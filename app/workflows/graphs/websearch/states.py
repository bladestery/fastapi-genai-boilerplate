"""Graph schema for the LangGraph-based application."""

import re
import uuid
from typing import Annotated

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, field_validator


class GraphState(BaseModel):
    """Defines the state for LangGraph workflows."""

    messages: Annotated[list, add_messages] = Field(
        default_factory=list, description="Conversation messages"
    )
    session_id: str = Field(..., description="Unique session identifier")

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Validates session_id as UUID or safe pattern."""
        try:
            uuid.UUID(v)
        except ValueError as exc:
            if not re.match(r"^[a-zA-Z0-9_\-]+$", v):
                raise ValueError(
                    "Session ID must be a valid UUID or contain only alphanumeric characters, underscores, and hyphens"
                ) from exc
        return v
