"""Mapping of tasks to their corresponding LLM model names."""

import enum


class LLMModelMap(str, enum.Enum):
    """Enum mapping specific agent tasks to their respective LLM model identifiers."""

    QUESTION_REWRITER = "gemini-2.5-flash"
    QUESTION_ENHANCER = "gemini-2.5-flash"
    ANSWER_GENERATOR = "gemini-2.5-flash"
