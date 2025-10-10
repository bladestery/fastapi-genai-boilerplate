"""Question enhancement component for generating multiple refined websearch questions."""

from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
from pydantic import BaseModel, Field

from app import settings

from ..local_model_client import LocalModelClient
from ..model_map import LLMModelMap
from ..states import AgentState


class EnhancedQuestionsResult(BaseModel):
    """
    Output schema representing multiple refined questions derived from the original query,
    aimed at maximizing the breadth and precision of a web search.
    """

    refined_questions: list[str] = Field(
        description="List of enhanced, standalone refined_questions for web search. Should include exactly 2 distinct and optimized questions."
    )


class QuestionEnhancer:
    """Agent component responsible for expanding a single query into multiple precise search questions."""

    def __init__(self):
        if settings.USE_LOCAL_MODEL:
            self.llm = LocalModelClient()
        else:
            from langchain_openai import ChatOpenAI
            from pydantic import SecretStr

            self.llm = ChatOpenAI(
                model=LLMModelMap.QUESTION_ENHANCER,
                api_key=SecretStr(settings.OPENAI_API_KEY),
            ).with_structured_output(
                schema=EnhancedQuestionsResult,
                strict=True,
            )

    def enhance(self, state: AgentState) -> dict:
        """
        Enhances a question into multiple standalone questions for better web search coverage.
        """

        question = (
            state["refined_question"]
            if state.get("refined_question")
            else state["question"].content
        )

        conversation = [
            SystemMessage(
                content=(
                    "You are a helpful assistant that rewrites a single complex question "
                    "into two standalone, web-search-friendly questions for broader and more precise retrieval. "
                    "Respond with exactly 2 questions, one per line."
                )
            ),
            HumanMessage(content=question),
        ]

        logger.info(
            f"Enhancing question with {'local' if settings.USE_LOCAL_MODEL else 'OpenAI'} model..."
        )

        if settings.USE_LOCAL_MODEL:
            response_content = self.llm.invoke(conversation)

            # Parse the response to extract questions
            lines = response_content.strip().split("\n")
            refined_questions = [line.strip() for line in lines if line.strip()][:2]

            # Ensure we have exactly 2 questions
            while len(refined_questions) < 2:
                refined_questions.append(
                    f"Enhanced question {len(refined_questions) + 1}"
                )

            response = EnhancedQuestionsResult(refined_questions=refined_questions[:2])
        else:
            from langchain_core.prompts import ChatPromptTemplate

            enhancer_prompt = ChatPromptTemplate.from_messages(conversation)
            response_data = (enhancer_prompt | self.llm).invoke({})
            response = EnhancedQuestionsResult.model_validate(response_data)

        logger.info(f"Generated enhanced questions: {response.refined_questions}")

        return {"refined_questions": response.refined_questions}
