"""Utility client for interacting with Gemini models hosted on Vertex AI."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any, Type

import google.genai as genai
from google.genai.types import Content, GenerateContentConfig, Part, Schema
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from loguru import logger
from pydantic import BaseModel, ValidationError

from app import settings


_ROLE_MAP = {
    SystemMessage: "user",
    HumanMessage: "user",
    AIMessage: "model",
}


class VertexGeminiClient:
    """Thin wrapper around the Google Generative AI Vertex client.

    The helper converts LangChain message objects into the structure expected by the
    ``google-genai`` SDK and optionally applies structured output schemas derived from
    Pydantic models.
    """

    def __init__(
        self,
        *,
        model: str,
        temperature: float = 0.0,
        max_output_tokens: int | None = None,
        top_k: int | None = None,
        top_p: float | None = None,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.top_k = top_k
        self.top_p = top_p
        self._client = genai.Client(
            vertexai=True,
            project=settings.PROJECT_ID or None,
            location=settings.REGION or None,
        )

    def invoke(self, messages: list[BaseMessage], *, stream: bool = False) -> str:
        """Generate a text response from Gemini."""

        config = self._build_config()
        response = self._client.models.generate_content(
            model=self.model,
            contents=self._convert_messages(messages),
            config=config
        )
        output_text = response.text.strip()
        logger.debug("Vertex AI response received", output=output_text)
        return output_text

    def invoke_structured(
        self, messages: list[BaseMessage], schema: Type[BaseModel]
    ) -> BaseModel:
        """Generate a structured response that conforms to ``schema``."""

        
        json_schema = schema.model_json_schema()
        config = self._build_config(response_schema=json_schema)
        
        response = self._client.models.generate_content(
            model=self.model,
            contents=self._convert_messages(messages),
            config=config,
        )
        #logger.debug(self._convert_messages(messages))
        raw_output = response.text.strip()
        logger.debug("Vertex AI structured response", output=raw_output)

        if not raw_output:
            logger.error("Empty response received from Vertex AI for structured call")
            raise ValueError("Vertex AI returned an empty response.")

        try:
            payload = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse structured output", error=str(exc))
            raise

        try:
            return schema.model_validate(payload)
        except ValidationError as exc:
            logger.error("Structured output validation error", error=str(exc))
            raise

    def _build_config(self, response_schema: dict[str, Any] | None = None) -> GenerateContentConfig:
        """Build a ``GenerateContentConfig`` with optional structured output schema."""

        config_kwargs: dict[str, Any] = {
            "temperature": self.temperature,
        }
        if self.max_output_tokens is not None:
            config_kwargs["max_output_tokens"] = self.max_output_tokens
        if self.top_k is not None:
            config_kwargs["top_k"] = self.top_k
        if self.top_p is not None:
            config_kwargs["top_p"] = self.top_p

        if response_schema is not None:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = self._convert_schema(response_schema)

        return GenerateContentConfig(**config_kwargs)

    @staticmethod
    def _convert_messages(messages: Iterable[BaseMessage]) -> list[Content]:
        contents: list[Content] = []
        for message in messages:
            role = VertexGeminiClient._resolve_role(message)
            text = VertexGeminiClient._extract_text(message)
            contents.append(
                Content(
                    role=role,
                    parts=[Part.from_text(text=text)],
                )
            )
        return contents

    @staticmethod
    def _resolve_role(message: BaseMessage) -> str:
        for klass, role in _ROLE_MAP.items():
            if isinstance(message, klass):
                return role
        return "user"

    @staticmethod
    def _extract_text(message: BaseMessage) -> str:
        if isinstance(message.content, str):
            return message.content
        if isinstance(message.content, list):
            # Join textual parts from LangChain message content lists.
            return "\n".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in message.content
            )
        return str(message.content)

    @staticmethod
    def _convert_schema(schema_dict: dict[str, Any]) -> Schema:
        """Recursively convert a JSON schema dict to a Vertex ``Schema``."""

        schema_type = schema_dict.get("type", "object")
        schema_description = schema_dict.get("description")
        if schema_type == "object":
            properties = schema_dict.get("properties", {})
            required = schema_dict.get("required", [])
            return Schema(
                type='OBJECT',
                description=schema_description,
                properties={
                    key: VertexGeminiClient._convert_schema(value)
                    for key, value in properties.items()
                },
                required=required,
            )
        if schema_type == "array":
            items_schema = schema_dict.get("items", {"type": "string"})
            return Schema(
                type='ARRAY',
                description=schema_description,
                items=VertexGeminiClient._convert_schema(items_schema),
            )
        if schema_type == "boolean":
            return Schema(type='BOOLEAN', description=schema_description)
        if schema_type == "integer":
            return Schema(type='INTEGER', description=schema_description)
        if schema_type == "number":
            return Schema(type='NUMBER', description=schema_description)
        # Default to string for unknown primitive types.
        return Schema(type='STRING', description=schema_description)