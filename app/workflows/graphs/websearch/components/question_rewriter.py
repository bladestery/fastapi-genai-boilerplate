"""Question rewriter components"""

from typing import Dict
from venv import logger

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, SecretStr

from app import settings

from ..model_map import LLMModelMap
from ..states import AgentState


class RefinedQueryResult(BaseModel):
    """
    Output schema representing the improved version of a user's question,
    tailored for better clarity and effectiveness in downstream tasks like web search or retrieval.
    """

    refined_question: str = Field(
        description="The user's original question, rewritten for improved clarity and optimized for retrieval tasks such as web search."
    )
    require_enhancement: bool = Field(
        description="Indicates whether the input question required refinement due to ambiguity or complexity."
    )


class QuestionRewriter:
    """Agent component responsible for improving user queries for better searchability."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=LLMModelMap.QUESTION_REWRITER,
            api_key=SecretStr(settings.OPENAI_API_KEY),
        ).with_structured_output(
            schema=RefinedQueryResult,
            strict=True,
        )

    def rewrite(self, state: AgentState) -> Dict:
        """
        Rewrites the question using chat history for context.
        """

        conversation = state["messages"][:-1] if len(state["messages"]) > 1 else []

        current_question = state["question"].content
        conversation.insert(
            0,
            SystemMessage(
                content="You are a helpful assistant that rephrases the user's question to be a standalone question optimized for websearch."
            ),
        )
        conversation.append(HumanMessage(content=current_question))
        rephrase_prompt = ChatPromptTemplate.from_messages(conversation)

        logger.info(f"Prompt constructed: {rephrase_prompt}")

        response_data = (rephrase_prompt | self.llm).invoke({})
        response = RefinedQueryResult.model_validate(response_data)

        refined_question = response.refined_question
        require_enhancement = response.require_enhancement

        logger.info(f"Refined question: {refined_question}")
        logger.info(f"Enhancement required: {require_enhancement}")

        return {
            "refined_question": refined_question,
            "require_enhancement": require_enhancement,
        }
