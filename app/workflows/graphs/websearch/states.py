"""Graph schema for the LangGraph-based application."""

import operator
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage


class AgentState(TypedDict):
    """The state of the agent throughout the reasoning process."""

    question: HumanMessage
    refined_question: str
    require_enhancement: bool
    refined_questions: list[str]
    search_results: list[dict]
    messages: Annotated[list[BaseMessage], operator.add]
