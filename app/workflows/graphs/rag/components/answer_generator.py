"""Answer generation component using rag search content and rephrased user question."""

from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.config import get_stream_writer
from loguru import logger

from app import settings

from ..local_model_client import LocalModelClient
from ..model_map import LLMModelMap
from ..prompts import RAG_PROMPT, SYSTEM_PROMPT
from ..states import AgentState
from .vertex_gemini_client import VertexGeminiClient


class AnswerGenerator:
    """Agent component responsible for synthesizing a final answer from retrieved rag content."""

    def __init__(self) -> None:
        if settings.USE_LOCAL_MODEL:
            self.llm = LocalModelClient()
        else:
            #from langchain_openai import ChatOpenAI
            #from pydantic import SecretStr

            #self.llm = ChatOpenAI(
            #    model=LLMModelMap.ANSWER_GENERATOR,
            #    api_key=SecretStr(settings.OPENAI_API_KEY),
            #)

            # from langchain_google_genai import ChatGoogleGenerativeAI

            # self.llm = ChatGoogleGenerativeAI(
            #     model=LLMModelMap.ANSWER_GENERATOR,
            #     temperature=0,
            #     max_tokens=None,
            #     timeout=None,
            #     max_retries=2,
            #     # other params...
            # )

            self.llm = VertexGeminiClient(
                model=LLMModelMap.ANSWER_GENERATOR.value,
                temperature=0.0,
            )

    def generate(self, state: AgentState) -> dict[str, list[AIMessage]]:
        """Generates an answer using retrieved rag content and the user's refined question."""

        rag_results = state["search_results"]
        result_blocks = {}
        combined_content = ""

        cnt = 1
        for result in rag_results:
            content = result.get("content")
            if content is not None:
                result_blocks[str(cnt)] = result
                cnt += 1

        for key, result in result_blocks.items():
            content = result.get("content", "")
            combined_content += f"{key}. {content}\n\n"

        # Stream citation
        writer = get_stream_writer()
        writer({"citation_map": result_blocks})

        rag_prompt = RAG_PROMPT.format(
            context=combined_content, question=state["question"].content
        )
        logger.debug(f"Aggregated content for answer generation:\n{rag_prompt}")

        # Prepare conversation history
        conversation = state["messages"][:-1] if len(state["messages"]) > 1 else []
        conversation.insert(
            0,
            SystemMessage(
                content=SYSTEM_PROMPT.format(
                    current_date_and_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            ),
        )
        conversation.append(HumanMessage(content=rag_prompt))

        logger.info(
            f"Generating answer with {'local' if settings.USE_LOCAL_MODEL else 'Vertex AI'} model..."
        )

        if settings.USE_LOCAL_MODEL:
            answer_content = self.llm.invoke(conversation)
        else:
            # prompt = ChatPromptTemplate.from_messages(conversation)
            # answer = self.llm.invoke(prompt.format())
            # answer_content = answer.content
            answer_content = self.llm.invoke(conversation)

        logger.info(f"Final Answer Generated:\n{answer_content}")

        return {"messages": [AIMessage(content=answer_content)]}
