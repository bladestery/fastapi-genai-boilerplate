"""Answer generation component using web search content and rephrased user question."""

from typing import Dict, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import SecretStr

from app import settings

from ..model_map import LLMModelMap
from ..states import AgentState


class AnswerGenerator:
    """Agent component responsible for synthesizing a final answer from retrieved web content."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=LLMModelMap.ANSWER_GENERATOR,
            api_key=SecretStr(settings.OPENAI_API_KEY),
        )

    def generate(self, state: AgentState) -> Dict[str, List[AIMessage]]:
        """
        Generates an answer using retrieved web content and the user's refined question.
        """
        web_results = state["search_results"]
        content_blocks = []

        for result in web_results:
            content = result.get("content")
            if content is not None:
                content_blocks.append(content)

        full_content = "\n---------\n".join(content_blocks)
        logger.debug(f"Aggregated content for answer generation:\n{full_content}")

        # Prepare conversation history
        conversation = state["messages"][:-1] if len(state["messages"]) > 1 else []
        conversation.insert(
            0,
            SystemMessage(
                content="You are a helpful assistant that gives accurate and concise answers based on web search content."
            ),
        )

        refined_question = state["refined_question"]
        conversation.append(
            HumanMessage(
                content=f"Content:\n{full_content}\n\nQuestion: {refined_question}"
            )
        )

        prompt = ChatPromptTemplate.from_messages(conversation)
        response = self.llm.invoke(prompt.format())
        answer = response.content

        logger.info(f"Final Answer Generated:\n{answer}")

        return {"messages": [AIMessage(content=answer)]}
