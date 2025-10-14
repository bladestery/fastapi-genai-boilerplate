"""Question rewriter components"""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger
from pydantic import BaseModel, Field

from app import settings

from ..local_model_client import LocalModelClient
from ..model_map import LLMModelMap
from ..states import AgentState

from ..prompts import QUESTION_REWRITER_PROMPT


class RefinedQueryResult(BaseModel):
    """
    Output schema representing the improved version of a user's question,
    tailored for better clarity and effectiveness in downstream tasks like web search or rag retrieval.
    """

    refined_question: str = Field(
        description="The user's original question, rewritten for improved clarity and optimized for retrieval tasks such as web search and rag."
    )
    require_enhancement: bool = Field(
        description="Indicates whether the input question required refinement and websearch due to ambiguity or complexity."
    )
    require_tripitika: bool = Field(
        description="Indicates whether the input question required retrieval augmented generation due to being domain specific on Thai tripitika text."
    )


class QuestionRewriter:
    """Agent component responsible for improving user queries for better searchability."""

    def __init__(self) -> None:
        if settings.USE_LOCAL_MODEL:
            self.llm = LocalModelClient()
        else:
            #from langchain_openai import ChatOpenAI
            #from pydantic import SecretStr

            #self.llm = ChatOpenAI(
            #    model=LLMModelMap.QUESTION_REWRITER,
            #    api_key=SecretStr(settings.OPENAI_API_KEY),
            #).with_structured_output(
            #    schema=RefinedQueryResult,
            #    strict=True,
            #)
            from langchain_google_genai import ChatGoogleGenerativeAI
            import google.auth

            credentials, project = google.auth.default(
                scopes=['https://www.googleapis.com/auth/cloud-platform', 'https://generativelanguage.googleapis.com']
            )

            self.llm = ChatGoogleGenerativeAI(
                model=LLMModelMap.QUESTION_REWRITER,
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                # other params...
            ).with_structured_output(
                schema=RefinedQueryResult,
                strict=True,
            )

    @staticmethod
    def delete_messages(state: AgentState) -> dict[str, list]:
        """Removes all messages except the last 10 from the conversation state."""
        messages = state["messages"]
        if len(messages) <= 10:
            return {"messages": messages}

        # Keep only the last 10 messages and update the state in-place to reflect
        # the removal.  We return a copy of the truncated list so downstream
        # consumers never see ``RemoveMessage`` instructions which previously
        # triggered ``ValueError`` while iterating over the conversation history.
        truncated_messages = list(messages[-10:])
        state["messages"] = truncated_messages
        return {"messages": truncated_messages}

    def rewrite(self, state: AgentState) -> dict:
        """
        Rewrites the question using chat history for context.
        """

        conversation = state["messages"][:-1] if len(state["messages"]) > 1 else []
        conversation = self.delete_messages(state=state)["messages"]

        current_question = state["question"].content
        conversation.insert(
            0,
            SystemMessage(
                content=QUESTION_REWRITER_PROMPT
            ),
        )
        conversation.append(HumanMessage(content=current_question))

        logger.info(
            f"Rewriting question with {'local' if settings.USE_LOCAL_MODEL else 'Vertex AI'} model..."
        )

        if settings.USE_LOCAL_MODEL:
            # For local models, we'll use a simpler approach
            response_content = self.llm.invoke(conversation)

            # Simple parsing for local models
            refined_question = response_content.strip()
            require_enhancement = (
                "complex" in response_content.lower()
                or "enhance" in response_content.lower()
            )
            require_triptika = (
                "tripitika" in response_content.lower()
                or "thai" in response_content.lower()
            )

            response = RefinedQueryResult(
                refined_question=refined_question,
                require_enhancement=require_enhancement,
                require_tripitika=require_tripitika
            )
        else:
            rephrase_prompt = ChatPromptTemplate.from_messages(conversation)
            response_data = (rephrase_prompt | self.llm).invoke({})
            response = RefinedQueryResult.model_validate(response_data)

        refined_question = response.refined_question
        require_enhancement = response.require_enhancement
        require_tripitika = response.require_tripitika

        logger.info(f"Refined question: {refined_question}")
        logger.info(f"Enhancement required: {require_enhancement}")
        logger.info(f"Tripitika required: {require_tripitika}")

        return {
            "refined_question": refined_question,
            "require_enhancement": require_enhancement,
            "require_tripitika" : require_tripitika
        }
