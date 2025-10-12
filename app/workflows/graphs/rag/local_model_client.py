"""Local model client for LM Studio integration."""

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel

from app import settings


class LocalModelClient:
    """Client for interacting with local LM Studio model."""

    def __init__(self) -> None:
        self.client = ChatOpenAI(
            base_url=settings.LOCAL_MODEL_URL + "/v1",
            api_key="not-needed",  # LM Studio doesn't require API key
            model="local-model",  # Model name doesn't matter for local
            temperature=0.7,
            max_tokens=2000,
        )

    def invoke(self, messages: list[BaseMessage]) -> str:
        """Invoke the local model with messages."""
        try:
            response = self.client.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error invoking local model: {e}")
            return "I apologize, but I encountered an error processing your request."

    def invoke_with_structured_output(
        self, messages: list[BaseMessage], schema: BaseModel
    ) -> BaseModel:
        """Invoke the local model with structured output."""
        try:
            # For local models, we'll use a simpler approach
            response = self.client.invoke(messages)
            content = response.content

            # Parse the response to extract structured data
            # This is a simplified approach - you might need to adjust based on your model's output format
            return self._parse_structured_response(content, schema)
        except Exception as e:
            logger.error(f"Error invoking local model with structured output: {e}")
            # Return default values
            return schema.model_validate({})

    def _parse_structured_response(self, content: str, schema: BaseModel) -> BaseModel:
        """Parse the model response to extract structured data."""
        # This is a simplified parser - you might need to adjust based on your model's output
        try:
            # Try to extract JSON-like content
            import json
            import re

            # Look for JSON in the response
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return schema.model_validate(data)

            # Fallback: try to extract key-value pairs
            data = {}
            for field in schema.model_fields:
                # Simple extraction - you might need more sophisticated parsing
                if field in content.lower():
                    data[field] = "extracted_value"  # Simplified

            return schema.model_validate(data)
        except Exception as e:
            logger.warning(f"Failed to parse structured response: {e}")
            return schema.model_validate({})
