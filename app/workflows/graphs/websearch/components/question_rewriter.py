"""Question rewriter components"""

from typing import Dict, List

from langchain_core.messages import HumanMessage, RemoveMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger
from pydantic import BaseModel, Field

from app import settings
from ..local_model_client import LocalModelClient
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
        if settings.USE_LOCAL_MODEL:
            self.llm = LocalModelClient()
        else:
            from langchain_openai import ChatOpenAI
            from pydantic import SecretStr
            self.llm = ChatOpenAI(
                model=LLMModelMap.QUESTION_REWRITER,
                api_key=SecretStr(settings.OPENAI_API_KEY),
            ).with_structured_output(
                schema=RefinedQueryResult,
                strict=True,
            )

    @staticmethod
    def delete_messages(state: AgentState) -> Dict[str, List]:
        """Removes all messages except the last 10 from the conversation state."""
        messages = state["messages"]
        if len(messages) > 10:
            # Keep only the last 10 messages
            to_remove = messages[:-10]  # All except last 10
            return {"messages": [RemoveMessage(id=m.id) for m in to_remove]}
        else:
            return {"messages": messages}

    def rewrite(self, state: AgentState) -> Dict:
        """
        Rewrites the question using chat history for context.
        """

        conversation = state["messages"][:-1] if len(state["messages"]) > 1 else []
        conversation = self.delete_messages(state=state)["messages"]

        current_question = state["question"].content
        conversation.insert(
            0,
            SystemMessage(
                content="You are a helpful assistant that rephrases the user's question to be a standalone question optimized for websearch."
            ),
        )
        conversation.append(HumanMessage(content=current_question))

        logger.info(f"Rewriting question with {'local' if settings.USE_LOCAL_MODEL else 'OpenAI'} model...")

        if settings.USE_LOCAL_MODEL:
            # For local models, we'll use a simpler approach
            response_content = self.llm.invoke(conversation)
            
            # Simple parsing for local models
            refined_question = response_content.strip()
            require_enhancement = "complex" in response_content.lower() or "enhance" in response_content.lower()
            
            response = RefinedQueryResult(
                refined_question=refined_question,
                require_enhancement=require_enhancement
            )
        else:
            rephrase_prompt = ChatPromptTemplate.from_messages(conversation)
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
